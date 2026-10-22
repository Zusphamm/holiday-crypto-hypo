"""
Holiday hypothesis test for BTC / ETH (standalone: only public Binance + Deribit APIs, no keys).

  pip install pandas numpy requests matplotlib
  python holiday_hypo_test.py                 # download (cached in ./holiday_cache), measure, test, plot
  python holiday_hypo_test.py --refresh       # re-download the data

Holidays (UTC date D): Christmas 12-25, New Year 01-01, US Thanksgiving, Easter (D = Good Friday), Lunar New Year,
US Independence Day 07-04, China Golden Week 10-01.

1. Measure: on day D (and 3 days before / after), $ volume, realised vol (sqrt of the sum of squared 1h log returns)
   and daily range vs the same weekday in the 8 weeks before (1.0 = normal).
2. PRE|ETH: long ETH perp from close D-4 to close D-1 on every holiday (16 bp round trip + funding), compared with a
   3-day ETH long on any day.
3. VOL: on Western holidays (Christmas, New Year, Easter, Thanksgiving) sell a 3-day ATM straddle at 00:00 UTC on D,
   priced at Deribit DVOL (30-d implied vol) with premium = 0.8 * IV * sqrt(3/365); payoff |S(D+3) / S0 - 1|;
   cost 0.06% of spot + 5% of premium. Compared with selling the same straddle every day.
   "break-even IV" = how far below DVOL the real holiday option price may be before the edge is gone.
   DVOL is a 30-day IV: real short-dated holiday options are usually priced lower, so this is the best case.

Periods: IS 2020-02 .. 2022-12 (DVOL from 2021-03-24), OS 2023-01 .. 2026-06-30.
"""
import math, sys, time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
CACHE = HERE / "holiday_cache"
START, OS0, END = pd.Timestamp("2020-01-01"), pd.Timestamp("2023-01-01"), pd.Timestamp("2026-07-01")
ASSETS = ("BTCUSDT", "ETHUSDT")
COST = 2 * (0.0005 + 0.0003)                                         # perp: taker 5 bp + slippage 3 bp, per side
EASTER = ["2020-04-12", "2021-04-04", "2022-04-17", "2023-04-09", "2024-03-31", "2025-04-20", "2026-04-05"]
LNY = ["2020-01-25", "2021-02-12", "2022-02-01", "2023-01-22", "2024-02-10", "2025-01-29", "2026-02-17"]
WEST = ("Christmas", "New Year", "Easter", "Thanksgiving")
ms = lambda t: int(t.timestamp() * 1000)


# ----------------------------------------------------------------------------- data
def get(url, **p):
    for i in range(5):
        try:
            r = requests.get(url, params=p, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"failed: {url} {p}")


def klines(sym, interval):
    f = CACHE / f"{sym}_{interval}.parquet"
    if f.exists() and "--refresh" not in sys.argv:
        return pd.read_parquet(f)
    step = {"1d": 86_400_000, "1h": 3_600_000}[interval]
    rows, t = [], ms(START)
    while t < ms(END):
        k = get("https://fapi.binance.com/fapi/v1/klines", symbol=sym, interval=interval, startTime=t, endTime=ms(END) - 1, limit=1500)
        if not k:
            break
        rows += k
        t = int(k[-1][0]) + step
        time.sleep(0.1)
    d = pd.DataFrame(rows).iloc[:, [0, 2, 3, 4, 7]]
    d.columns = ["t", "high", "low", "close", "quote_volume"]
    d.index = pd.to_datetime(d.t, unit="ms")
    d = d.drop(columns="t").astype(float)
    d = d[~d.index.duplicated()]
    d.to_parquet(f)
    return d


def funding(sym):
    f = CACHE / f"{sym}_funding.parquet"
    if f.exists() and "--refresh" not in sys.argv:
        return pd.read_parquet(f).rate
    rows, t = [], ms(START)
    while t < ms(END):
        r = get("https://fapi.binance.com/fapi/v1/fundingRate", symbol=sym, startTime=t, endTime=ms(END) - 1, limit=1000)
        if not r:
            break
        rows += r
        t = int(r[-1]["fundingTime"]) + 1
        time.sleep(0.1)
    s = pd.Series({pd.Timestamp(int(x["fundingTime"]), unit="ms"): float(x["fundingRate"]) for x in rows}, name="rate").sort_index()
    s.to_frame().to_parquet(f)
    return s


def dvol(cur):
    f = CACHE / f"dvol_{cur}.parquet"
    if f.exists() and "--refresh" not in sys.argv:
        return pd.read_parquet(f).close
    rows, end = [], ms(END) - 1
    while True:
        r = get("https://www.deribit.com/api/v2/public/get_volatility_index_data", currency=cur,
                start_timestamp=ms(pd.Timestamp("2021-01-01")), end_timestamp=end, resolution="1D")["result"]
        rows += r["data"]
        if not r.get("continuation") or not r["data"]:
            break
        end = r["continuation"]
        time.sleep(0.3)
    s = pd.DataFrame(rows, columns=["t", "open", "high", "low", "close"]).drop_duplicates("t")
    s.index = pd.to_datetime(s.t, unit="ms")
    s = s.sort_index()[["close"]]
    s = s[s.index < END]
    s.to_parquet(f)
    return s.close


# ----------------------------------------------------------------------------- calendar
def thanksgiving(y):
    d = pd.Timestamp(f"{y}-11-01")
    return d + pd.Timedelta(days=(3 - d.weekday()) % 7 + 21)


def holidays():
    H = []
    for y in range(2020, 2027):
        H += [("Christmas", pd.Timestamp(f"{y}-12-25")), ("New Year", pd.Timestamp(f"{y}-01-01")),
              ("Thanksgiving", thanksgiving(y)), ("July 4", pd.Timestamp(f"{y}-07-04")),
              ("Golden Week", pd.Timestamp(f"{y}-10-01"))]
    H += [("Easter", pd.Timestamp(e) - pd.Timedelta(days=2)) for e in EASTER]
    H += [("Lunar New Year", pd.Timestamp(d)) for d in LNY]
    return sorted([(n, d) for n, d in H if START + pd.Timedelta(days=60) <= d and d + pd.Timedelta(days=4) < END - pd.Timedelta(days=1)],
                  key=lambda x: x[1])


seg = lambda d: "IS" if d < OS0 else "OS"


# ----------------------------------------------------------------------------- 1. measure
def measure(D1, H1):
    H = holidays()
    excl = {D + pd.Timedelta(days=k) for _, D in H for k in range(-4, 5)}
    rows = []
    for a in ASSETS:
        d = D1[a].copy()
        lr = np.log(H1[a].close).diff()
        d["rv"] = np.sqrt((lr ** 2).groupby(lr.index.floor("D")).sum(min_count=20)).reindex(d.index)
        d["rng"] = (d.high - d.low) / d.close
        for name, D in H:
            r = dict(holiday=name, date=D.date(), seg=seg(D), asset=a)
            for w, ks in (("pre", range(-3, 0)), ("hol", [0]), ("post", range(1, 4))):
                for m in ("quote_volume", "rv", "rng"):
                    vals = []
                    for x in (D + pd.Timedelta(days=k) for k in ks):
                        base = [x - pd.Timedelta(weeks=k) for k in range(1, 9)]
                        b = d[m].reindex([y for y in base if y not in excl]).median()
                        if np.isfinite(b) and b > 0 and x in d.index:
                            vals.append(d.at[x, m] / b)
                    r[f"{w}_{m}"] = np.nanmean(vals) if vals else np.nan
            rows.append(r)
    M = pd.DataFrame(rows)
    print("\n=== 1. Holiday day vs normal (same weekday, 8 weeks before); 1.0 = normal ===")
    t = M.groupby(["holiday", "seg"])[["hol_quote_volume", "hol_rv", "hol_rng", "post_rv"]].mean().unstack("seg").round(2)
    t.columns = [f"{a.replace('hol_', 'day_').replace('quote_volume', 'volume')}_{b}" for a, b in t.columns]
    print(t.to_string())
    return M


# ----------------------------------------------------------------------------- 2. PRE|ETH
def pre_eth(D1, F):
    c, f = D1["ETHUSDT"].close, F["ETHUSDT"].cumsum()
    fat = lambda t: float(f[f.index <= t].iloc[-1]) if (f.index <= t).any() else 0.0
    rows = []
    for name, D in holidays():
        t0, t1 = D - pd.Timedelta(days=4), D - pd.Timedelta(days=1)       # bar dates; close of bar t = price at t + 1 day
        if t0 in c.index and t1 in c.index:
            net = c[t1] / c[t0] - 1 - (fat(t1 + pd.Timedelta(days=1)) - fat(t0 + pd.Timedelta(days=1))) - COST
            rows.append(dict(holiday=name, date=D, seg=seg(D), net=net))
    X = pd.DataFrame(rows)
    base = (c.shift(-3) / c - 1 - COST).dropna()
    print("\n=== 2. PRE|ETH: long ETH close D-4 -> close D-1 ===")
    for s in ("IS", "OS"):
        x = X[X.seg == s].net
        b = base[(base.index < OS0) if s == "IS" else (base.index >= OS0)]
        print(f"{s}: {len(x)} trades | win {(x > 0).mean():.0%} | mean {x.mean() * 100:+.2f}% | median {x.median() * 100:+.2f}% "
              f"| t {x.mean() / x.std() * math.sqrt(len(x)):.2f}   || any 3-day ETH long: win {(b > 0).mean():.0%} mean {b.mean() * 100:+.2f}%")
    return X


# ----------------------------------------------------------------------------- 3. VOL straddle
def vol_straddle(D1):
    hol = {D: n for n, D in holidays() if n in WEST}
    rows = []
    for a in ASSETS:
        iv, s = dvol(a[:3]) / 100, D1[a].close
        for d in iv.index:                                               # DVOL day-d close = IV at 00:00 d+1 = spot close of bar d
            d1 = d + pd.Timedelta(days=3)
            if d not in s.index or d1 not in s.index:
                continue
            prem = 0.8 * iv[d] * math.sqrt(3 / 365)
            move = abs(s[d1] / s[d] - 1)
            day = d + pd.Timedelta(days=1)
            rows.append(dict(asset=a[:3], day=day, seg=seg(day), holiday=hol.get(day), prem=prem, move=move,
                             pnl=prem - move - 0.0006 - 0.05 * prem))
    V = pd.DataFrame(rows)
    be = lambda g: (g.move.mean() + 0.0006) / (0.95 * g.prem.mean())
    print("\n=== 3. VOL: sell 3-day ATM straddle at 00:00 UTC on Western holidays (DVOL-priced, % of spot) ===")
    for (a, s), g in V.groupby(["asset", "seg"]):
        h, b = g[g.holiday.notna()], g[g.holiday.isna()]
        print(f"{a} {s}: {len(h)} holidays | win {(h.pnl > 0).mean():.0%} | mean {h.pnl.mean() * 100:+.2f}% | break-even IV "
              f"{be(h):.0%} of DVOL   || every day: win {(b.pnl > 0).mean():.0%} mean {b.pnl.mean() * 100:+.2f}% break-even {be(b):.0%}")
        print("      by holiday (mean %):", (h.groupby("holiday").pnl.mean() * 100).round(2).to_dict())
    return V


def plot(X, V):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8))
    for ax in (a1, a2):
        ax.axvspan(OS0, END, color="#f4d03f", alpha=0.15, lw=0)
        ax.axhline(0, color="gray", lw=0.6)
        ax.grid(alpha=0.3)
    x = X.sort_values("date")
    a1.plot(x.date, x.net.cumsum() * 100, marker="o", ms=3, drawstyle="steps-post")
    a1.set_title("PRE|ETH: long ETH 3 days before holidays")
    a1.set_ylabel("cumulative % (same size per trade)")
    h = V[V.holiday.notna()].sort_values("day")
    for a, g in h.groupby("asset"):
        a2.plot(g.day, g.pnl.cumsum() * 100, marker="o", ms=3, drawstyle="steps-post", label=a)
    a2.legend()
    a2.set_title("VOL: short 3-day ATM straddle over Western holidays (DVOL)")
    a2.set_ylabel("cumulative % of spot")
    fig.suptitle("Holiday hypotheses — yellow = OS 2023-01 .. 2026-06")
    plt.tight_layout()
    out = HERE / "holiday_hypo_test.png"
    plt.savefig(out, dpi=110)
    print(f"\nchart: {out}")


def main():
    CACHE.mkdir(exist_ok=True)
    print("downloading / loading data (first run takes a few minutes) ...")
    D1 = {a: klines(a, "1d") for a in ASSETS}
    H1 = {a: klines(a, "1h") for a in ASSETS}
    F = {a: funding(a) for a in ASSETS}
    measure(D1, H1)
    X = pre_eth(D1, F)
    V = vol_straddle(D1)
    plot(X, V)


if __name__ == "__main__":
    main()
