"""
Kiểm định giả thuyết ngày lễ cho BTC / ETH (chạy độc lập: chỉ dùng API công khai của Binance + Deribit, không cần key).

  pip install pandas numpy requests matplotlib
  python holiday_hypo_test.py                 # tải dữ liệu (cache trong ./holiday_cache), đo, kiểm định, vẽ biểu đồ
  python holiday_hypo_test.py --refresh       # tải lại dữ liệu

Ngày lễ (ngày D theo UTC): Giáng sinh 25/12, Năm mới 1/1, Lễ Tạ ơn Mỹ, Phục sinh (D = Thứ Sáu Tuần Thánh), Tết Nguyên
đán, Quốc khánh Mỹ 4/7, Quốc khánh Trung Quốc 1/10.

1. Đo lường: vào ngày D (và 3 ngày trước / sau), volume $, biến động thực (căn của tổng bình phương log return 1h)
   và biên độ ngày so với cùng thứ trong 8 tuần trước (1.0 = bình thường).
2. PRE|ETH: long ETH perp từ giá đóng cửa D-4 đến D-1 ở mọi ngày lễ (16 bp khứ hồi + funding), so với long ETH
   3 ngày vào một ngày bất kỳ.
3. VOL: vào các lễ phương Tây (Giáng sinh, Năm mới, Phục sinh, Lễ Tạ ơn) bán straddle ATM 3 ngày lúc 00:00 UTC ngày D,
   định giá theo Deribit DVOL (implied vol 30 ngày) với phí quyền chọn = 0.8 * IV * sqrt(3/365); trả |S(D+3) / S0 - 1|;
   chi phí 0.06% giá spot + 5% phí quyền chọn. So với bán cùng straddle mỗi ngày.
   "IV hoà vốn" = giá quyền chọn dịp lễ thật có thể thấp hơn DVOL bao nhiêu trước khi edge biến mất.
   DVOL là IV 30 ngày: quyền chọn ngắn hạn dịp lễ thật thường rẻ hơn, nên đây là trường hợp tốt nhất.

Giai đoạn: IS 2020-02 .. 2022-12 (DVOL từ 2021-03-24), OS 2023-01 .. 2026-06-30.
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
COST = 2 * (0.0005 + 0.0003)                                         # perp: taker 5 bp + trượt giá 3 bp, mỗi chiều
EASTER = ["2020-04-12", "2021-04-04", "2022-04-17", "2023-04-09", "2024-03-31", "2025-04-20", "2026-04-05"]
LNY = ["2020-01-25", "2021-02-12", "2022-02-01", "2023-01-22", "2024-02-10", "2025-01-29", "2026-02-17"]
WEST = ("Giáng sinh", "Năm mới", "Phục sinh", "Lễ Tạ ơn")
ms = lambda t: int(t.timestamp() * 1000)


# ----------------------------------------------------------------------------- dữ liệu
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


# ----------------------------------------------------------------------------- lịch
def thanksgiving(y):
    d = pd.Timestamp(f"{y}-11-01")
    return d + pd.Timedelta(days=(3 - d.weekday()) % 7 + 21)


def holidays():
    H = []
    for y in range(2020, 2027):
        H += [("Giáng sinh", pd.Timestamp(f"{y}-12-25")), ("Năm mới", pd.Timestamp(f"{y}-01-01")),
              ("Lễ Tạ ơn", thanksgiving(y)), ("Quốc khánh Mỹ 4/7", pd.Timestamp(f"{y}-07-04")),
              ("Quốc khánh TQ 1/10", pd.Timestamp(f"{y}-10-01"))]
    H += [("Phục sinh", pd.Timestamp(e) - pd.Timedelta(days=2)) for e in EASTER]
    H += [("Tết Nguyên đán", pd.Timestamp(d)) for d in LNY]
    return sorted([(n, d) for n, d in H if START + pd.Timedelta(days=60) <= d and d + pd.Timedelta(days=4) < END - pd.Timedelta(days=1)],
                  key=lambda x: x[1])


seg = lambda d: "IS" if d < OS0 else "OS"


# ----------------------------------------------------------------------------- 1. đo lường
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
    print("\n=== 1. Ngày lễ so với ngày thường (cùng thứ, 8 tuần trước); 1.0 = bình thường ===")
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
        t0, t1 = D - pd.Timedelta(days=4), D - pd.Timedelta(days=1)       # ngày của nến; giá đóng nến t = giá lúc t + 1 ngày
        if t0 in c.index and t1 in c.index:
            net = c[t1] / c[t0] - 1 - (fat(t1 + pd.Timedelta(days=1)) - fat(t0 + pd.Timedelta(days=1))) - COST
            rows.append(dict(holiday=name, date=D, seg=seg(D), net=net))
    X = pd.DataFrame(rows)
    base = (c.shift(-3) / c - 1 - COST).dropna()
    print("\n=== 2. PRE|ETH: long ETH từ giá đóng D-4 -> giá đóng D-1 ===")
    for s in ("IS", "OS"):
        x = X[X.seg == s].net
        b = base[(base.index < OS0) if s == "IS" else (base.index >= OS0)]
        print(f"{s}: {len(x)} lệnh | thắng {(x > 0).mean():.0%} | TB {x.mean() * 100:+.2f}% | trung vị {x.median() * 100:+.2f}% "
              f"| t {x.mean() / x.std() * math.sqrt(len(x)):.2f}   || long ETH 3 ngày bất kỳ: thắng {(b > 0).mean():.0%} TB {b.mean() * 100:+.2f}%")
    return X


# ----------------------------------------------------------------------------- 3. straddle VOL
def vol_straddle(D1):
    hol = {D: n for n, D in holidays() if n in WEST}
    rows = []
    for a in ASSETS:
        iv, s = dvol(a[:3]) / 100, D1[a].close
        for d in iv.index:                                               # DVOL đóng ngày d = IV lúc 00:00 d+1 = giá đóng nến d
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
    print("\n=== 3. VOL: bán straddle ATM 3 ngày lúc 00:00 UTC vào lễ phương Tây (định giá DVOL, % giá spot) ===")
    for (a, s), g in V.groupby(["asset", "seg"]):
        h, b = g[g.holiday.notna()], g[g.holiday.isna()]
        print(f"{a} {s}: {len(h)} ngày lễ | thắng {(h.pnl > 0).mean():.0%} | TB {h.pnl.mean() * 100:+.2f}% | IV hoà vốn "
              f"{be(h):.0%} DVOL   || mọi ngày: thắng {(b.pnl > 0).mean():.0%} TB {b.pnl.mean() * 100:+.2f}% hoà vốn {be(b):.0%}")
        print("      theo ngày lễ (TB %):", (h.groupby("holiday").pnl.mean() * 100).round(2).to_dict())
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
    a1.set_title("PRE|ETH: long ETH 3 ngày trước lễ")
    a1.set_ylabel("% cộng dồn (mỗi lệnh cùng khối lượng)")
    h = V[V.holiday.notna()].sort_values("day")
    for a, g in h.groupby("asset"):
        a2.plot(g.day, g.pnl.cumsum() * 100, marker="o", ms=3, drawstyle="steps-post", label=a)
    a2.legend()
    a2.set_title("VOL: bán straddle ATM 3 ngày qua lễ phương Tây (DVOL)")
    a2.set_ylabel("% giá spot cộng dồn")
    fig.suptitle("Giả thuyết ngày lễ — nền vàng = OS 2023-01 .. 2026-06")
    plt.tight_layout()
    out = HERE / "holiday_hypo_test.png"
    plt.savefig(out, dpi=110)
    print(f"\nbiểu đồ: {out}")


def main():
    CACHE.mkdir(exist_ok=True)
    print("đang tải / đọc dữ liệu (lần đầu mất vài phút) ...")
    D1 = {a: klines(a, "1d") for a in ASSETS}
    H1 = {a: klines(a, "1h") for a in ASSETS}
    F = {a: funding(a) for a in ASSETS}
    measure(D1, H1)
    X = pre_eth(D1, F)
    V = vol_straddle(D1)
    plot(X, V)


if __name__ == "__main__":
    main()
