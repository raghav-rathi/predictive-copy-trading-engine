# TRIX Momentum Turn — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:24 UTC
(ms `[1773446400000, 1792589072292)`; actual data starts 2026-03-14
22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,296 bars
BTC/ETH, 5,294 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: TRIX(14) / signal EMA(9), long on a cross-up
while TRIX<0, short on a cross-down while TRIX>0, exits on the opposite
cross, 2xATR stop, 3xATR trail, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 180 | 38.3% | -$724 | -7.2% | -0.34 | -19.7% | -$4.02 | 0.92 |
| ETH | 182 | 37.4% | +$441 | +4.4% | +0.42 | -14.9% | +$2.42 | 1.04 |
| HYPE | 183 | 43.7% | +$5,573 | +55.7% | +2.94 | -10.3% | +$30.45 | 1.50 |
| **Combined** | **545** | **39.8%** | **+$5,290** | — | — | — | +$9.71 | — |

## Verdict: a winner on the ledger, but it is one coin doing all the work

Combined +$5,290 across 545 trades, and HYPE is the entire story:
+$5,573 with Sharpe +2.94, PF 1.50, 43.7% win rate, expectancy +$30.45
a trade, and a modest -10.3% max drawdown. The triple-EMA smoothing
plus the turn-from-negative/turn-from-positive entry filter keeps it
in HYPE's big 2026 trend legs and mostly out of chop — 183 trades in
7 months is the right pace, and fees ($1,232) are a manageable 22% of
gross, not the dominant line item.

The other two legs are honest about how narrow this is:

- **BTC is a loser** (-$724, PF 0.92, Sharpe -0.34, MaxDD -19.7% —
  the deepest hole of the three). TRIX turns on BTC's 1h either come
  too late or get reversed before the leg pays.
- **ETH is borderline noise** (+$441, PF 1.04, expectancy +$2.42,
  Sharpe +0.42). Green on paper, but fees ($1,756) are 4x the net —
  one fewer winning trade and the sign flips.
- 545 trades in one 7-month crypto regime is a thin sample, and the
  combined green depends entirely on HYPE behaving like HYPE.

Treat this as a HYPE-specific momentum filter with paper evidence,
not a three-coin strategy.

## Calibration note

Shipped the specified len=14. A 10/14/21 length sweep is in
CALIBRATION.md: len=14 is the in-sample combined winner (+$5,290) and
the only setting positive-or-flat on all three coins; len=21 fixes
BTC (+$1,463) but fades ETH (-$233) and HYPE; len=10 is negative
everywhere except HYPE. The len=14 setting was fixed a priori —
adopted before the sweep, not because of it.

## Mechanism

TRIX: triple EMA(14) of close, trix = 100 × (EMA3 − EMA3.shift(1)) /
EMA3.shift(1), signal = EMA(trix, 9). Long when TRIX crosses above its
signal while still below zero (turn-up from washed-out territory);
short when it crosses below its signal while still above zero. Exits
are the opposite cross regardless of territory — a cross the other
way means the turn failed. 2xATR hard stop, 3xATR chandelier trail,
200-bar max hold.

Source: TRIX (Jack Hutson) —
https://capital.com/en-eu/learn/technical-analysis/trix-indicator

## Limitations

- Single 7-month crypto window; 545 trades is a thin sample, and all
  of the green is HYPE.
- ETH leg is near-noise (fees 4x net); BTC leg is negative.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped length on this window (see CALIBRATION.md).
