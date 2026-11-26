# Supertrend VWAP — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: Supertrend(10, 3.0) + UTC-day
session VWAP agreement; exit on Supertrend flip or VWAP
cross; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 818 | 19.9% | -$8,694 | -86.9% | -8.23 | -87.5% | -$10.63 | 0.45 |
| ETH | 847 | 22.1% | -$8,510 | -85.1% | -7.16 | -85.6% | -$10.05 | 0.49 |
| HYPE | 754 | 25.7% | -$5,908 | -59.1% | -4.15 | -63.1% | -$7.84 | 0.66 |
| **Combined** | **2,419** | **22.5%** | **-$23,112** | — | **-8.04** | **-78.1%** | **-$9.55** | **0.54** |

Fees: BTC $3,918, ETH $3,076, HYPE $2,437 (total $9,432).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL. Combined equity ends
at $6,887 on a $30,000 start — the worst result of batch 47.

## Verdict: the worst strategy of the batch — two lagging legs do not make a leading one

Combined −$23,112 on 2,419 trades (PF 0.54, Sharpe −8.04)
wipes out 77% of the combined equity, and every coin is
destroyed: BTC −86.9% (Sharpe −8.23, MaxDD −87.5%), ETH
−85.1%, HYPE −59.1%. Win rates 20–26% with PF 0.45–0.66.
The failure is structural, not parametric: the session VWAP
resets every UTC day, so the VWAP leg flips intraday as the
day's volume-weighted mean moves — it is a mean, not a
trend line — while Supertrend is a lagging ratchet that
flips only after price has already moved 3xATR against it.
Requiring both to agree does not filter chop, it
concentrates entries into the worst moments: price has
already run (Supertrend flipped late), then mean-reverts
toward the day's VWAP, and the exit fires after the move is
over. Signal exits dominate (577 / 572 / 602 vs 241 / 275 /
152 stops), so again the strategy's own exits bleed the
account out. Honest read: do not trade this. Agreement
between two lagging indicators is not confirmation.

## Mechanism

Supertrend(10, 3.0) via base.supertrend: ATR bands around
the bar midpoint (h+l)/2, ratcheted so the active band can
only move toward price, flipping state when a close crosses
the line; direction +1 is long, −1 short. Session VWAP via
base.anchored_vwap: typical price (h+l+c)/3 volume-weighted
since 00:00 UTC, resetting each UTC day. Long when
Supertrend is long and the close is above VWAP; short when
Supertrend is short and the close is below VWAP. Exit when
Supertrend flips or the close crosses VWAP against the
position. The harness 2xATR hard stop / 3xATR chandelier
trail sit behind the flip/VWAP-cross exit as a safety net
for gap-through moves; 120-bar max hold.

Source: Supertrend indicator (Olivier Seban) —
https://www.investopedia.com/supertrend-indicator-7976167
(verified via web search 2026-11-26; confirms the ATR-band
construction, the one-way ratchet, and the standard defaults
ATR 10 / multiplier 3).

## Limitations

- Single ~8.5-month crypto window; the verdict is negative on
  all three coins, so the failure is broad, not coin-specific.
- Level-condition entries re-enter the same agreement run
  after every exit; a flip-only (transition) entry would
  trade far less and was not tested here.
- The session VWAP resets daily, so the VWAP leg is an
  intraday mean, not a trend filter — the two legs measure
  different things on different horizons.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped Supertrend multiplier on this window.
