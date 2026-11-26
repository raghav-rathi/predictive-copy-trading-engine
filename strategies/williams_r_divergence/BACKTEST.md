# Williams %R Divergence — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=30 bars.

## Results (shipped config: %R(14) regular divergence on
confirmed ±2-bar pivots, %R < −80 / > −20 at the pivot;
exit on a %R cross back through −50 or the opposite
divergence; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 59 | 20.3% | -$1,693 | -16.9% | -2.86 | -17.4% | -$28.70 | 0.36 |
| ETH | 63 | 30.2% | -$1,593 | -15.9% | -2.91 | -15.9% | -$25.29 | 0.36 |
| HYPE | 67 | 29.9% | -$1,483 | -14.8% | -2.28 | -17.1% | -$22.13 | 0.50 |
| **Combined** | **189** | **27.0%** | **-$4,769** | — | **-4.43** | **-16.0%** | **-$25.23** | **0.41** |

Fees: BTC $529, ETH $443, HYPE $307 (total $1,279).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: the fewest trades, the worst hit rate — divergence catches falling knives

Combined -$4,769 on just 189 trades (PF 0.41, Sharpe
-4.43) is the smallest dollar loss of this batch's three
strategies only because it trades the least — per trade it
is the worst of the three (expectancy -$25.23, win rate
27.0%). The divergence idea fails cleanly on 1h crypto: a
lower low with a higher %R is usually a pause inside a
downtrend, not a turn, and the position is entered two bars
after the pivot confirms, into a market still falling.
Signal exits (34 / 39 / 39) outnumber stop exits (25 / 24 /
28), so most trades do reach the %R −50 exit — and still
lose, because the entry was already underwater by then.
The loss is even across coins (-$1,483 to -$1,693, PF
0.36–0.50), so this is not a coin-specific accident. Honest
read: do not trade this. Divergence needs the turn to
follow within hours; on this window it usually does not.

## Mechanism

%R(14) = −100 * (HH14 − close) / (HH14 − LL14); flat bars
read −50. Confirmed pivots follow macd_rsi_divergence
exactly: a pivot low at bar i−2 is confirmed at bar i when
its low is the strict lowest of the ±2-bar window. Bullish
divergence: confirmed pivot low lower than the previous one
while %R at the pivot is higher, with %R < −80 at the
pivot — long on the close of the confirming bar. Bearish is
the mirror with %R > −20. Exit: %R crosses back through
−50 against the position, or the opposite divergence
confirms (flip on the same bar). State machine: entries
only when flat, no re-entry while a position is held. The
harness 2xATR hard stop / 3xATR trail sit behind the %R
exit; 120-bar max hold.

Source: Larry Williams — Williams %R divergence —
https://en.wikipedia.org/wiki/Williams_%R

## Limitations

- Single ~8.4-month crypto window; the verdict is negative
  on all three coins, so no single-coin read generalises
  upward.
- Only 189 trades: the per-coin reads (59–67 trades) are
  thin, but all three agree, which is the point.
- The ±2-bar pivot confirmation lags the turn by design;
  on 1h bars the lag plus the %R −50 exit leave little
  room for the turn to pay.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped %R period on this window.
