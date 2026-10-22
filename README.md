# holiday-crypto-hypo

Holiday effect on BTC / ETH perpetuals, tested with public data only (Binance USDT-M klines + funding, Deribit DVOL).

## Run

```bash
pip install pandas numpy requests matplotlib pyarrow
python holiday_hypo_test.py            # downloads into ./holiday_cache on the first run (~1 min)
python holiday_hypo_test.py --refresh  # re-download
```

## What it tests

| Part | Rule |
|------|------|
| Measure | volume, realised vol (1h), daily range on holidays vs the same weekday in the 8 weeks before |
| PRE\|ETH | long ETH perp from close D-4 to close D-1 on 7 holidays a year (16 bp + funding) |
| VOL | sell a 3-day ATM straddle at 00:00 UTC on Christmas, New Year, Easter (Good Friday), Thanksgiving, priced at DVOL |

Holidays: Christmas, New Year, US Thanksgiving, Easter, Lunar New Year, July 4, China Golden Week.
Periods: IS 2020-02 .. 2022-12, OS 2023-01 .. 2026-06.

## Results (from the script)

| | IS | OS |
|---|---|---|
| Western holidays: realised vol vs normal | 0.70-0.82 | 0.45-0.68 |
| Asian holidays: realised vol vs normal | 0.74-1.01 | 1.25-2.17 |
| PRE\|ETH | 19 trades, win 74%, +0.81% | 24 trades, win 62%, +0.99% |
| VOL BTC (DVOL-priced) | 7, win 100%, +3.9% of spot | 14, win 79%, +2.1% |
| VOL ETH (DVOL-priced) | 7, win 100%, +3.6% | 14, win 79%, +2.0% |

## Caveats

- Small samples (7-24 events per period); no result reaches t >= 2 for the directional trade.
- DVOL is a 30-day implied vol. Real short-dated options over holidays are usually priced lower, so the VOL result is
  a best case: the edge disappears if holiday options trade below ~45% (BTC) / ~58% (ETH) of DVOL.
- Research only, not investment advice.

![chart](holiday_hypo_test.png)
