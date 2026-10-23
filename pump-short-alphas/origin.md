# origin

Where the two ideas came from, and where the anomaly is.

## How A / A* was found (machine-mined, 2026-10-22)

| Step | What happened |
|---|---|
| 1. Feature set | daily features per perp: returns (1d / 7d), open-interest change, funding, taker buy ratio, volume / range z-scores, distance from the 30-d high |
| 2. LLM proposes | a local LLM (Qwen3-8B) reads a leaderboard of past rules + recent misses and proposes a new rule, with 2 features forced per round |
| 3. Thresholds | code calibrates the thresholds to ~40 in-sample entries using signal counts only (no returns seen) |
| 4. IS test | backtest on 2021-2023: `oi_chg_7d <= -0.25 & ret_1d >= 0.13 -> short 7d, BTC hedge` = rule A, trial no. 417: 114 trades, 71% win, +3.6% per trade. It failed the strict checks (deflated Sharpe 0.08, one weak year) but passed the "hit" bar (n >= 15, win >= 65%, mean >= +2%) |
| 5. OS batch | 160 frozen rules run once on 2024-01 .. 2026-06; 25 passed (n >= 10, win >= 55%, mean >= +1%). A (+2.6%) and its sibling B (`oi <= -0.30 & ret_1d >= 0.15`, no hedge, +5.4%) were among them, but with single trades at -216% / -248% |
| 6. Tuning | 12,000 grid cells (OI cut, pump cut, hold, hedge, stop type, volatility filter) on IS and OS, aimed at a stop that lets price breathe but caps blow-ups. The OS had already been seen, so this step is not a clean holdout |
| 7. A* | hold 10d, no hedge, exit if a daily close is >= entry x 1.5, and skip coins whose 30-d daily-return std is > 0.12 (the OS blow-ups were coins with std 0.2-0.4) |

The LLM's own explanation was wrong: it read `oi_chg_7d` as a 7-day price drop. The rule was kept for its numbers;
the mechanism below was worked out afterwards.

## Where the anomaly is (A*)

| Normal pump | This pump |
|---|---|
| price +13% in a day comes with open interest rising: new leveraged longs chase it | open interest has **fallen >= 25% in 7 days**: positions are being closed, not opened |
| new money keeps buying | the buying is mostly forced: shorts covering (closing a short = a market buy, and it also lowers OI) or a thin order book squeezed |
| trend can continue | once covering is done, nobody is left to buy; price drifts back over the next days |

So the anomaly is the **divergence between price and positioning**: a big up-day with no new open interest behind it.
"Price up + OI down = short covering, a weak rally" is an old futures-market heuristic; the rule makes it testable on
perps. The volatility filter removes the cases where it fails worst: coins already in a mania, where the squeeze keeps
going. It works best when BTC is falling and volatile (OS 81% win, +9% per trade in that regime), where a lone alt pump
is even less likely to be real demand. This is the likely explanation, not a proven cause.

## How retail_crowded_long was found (hand-written, 2026-10-23)

| Step | What happened |
|---|---|
| Idea | one of 10 hand-written "who is forced to trade" seeds: after a strong week, retail piles into longs |
| Signal | Binance global long/short **account** ratio (counts accounts, not size: a retail-crowd gauge), as a z-score vs its own history, plus the 7-d return |
| Calibration | the seed was z >= 3 & ret_7d >= 30%; thresholds calibrated to 15-150 IS entries -> z >= 1.806 & ret_7d >= 24.95% |
| IS | 37 trades, 70% win, +7.3%, positive in every IS year |
| OS | 1 of 17 IS hits that passed the OS bar (302 trades, 68% win, +3.4%) |

Anomaly: after a +25% week, an unusually high share of accounts is long. Those are late, small, leveraged buyers;
there is little fresh demand left and many stops / liquidations below. The short bets that the crowded side unwinds.

## Related

- [README](README.md)
- [variants](variants.md)
