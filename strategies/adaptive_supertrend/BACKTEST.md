# Adaptive Supertrend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC
(ms `[1773525600000, 1792328400000)`): 5,223 bars BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start per coin. WARMUP=60 bars.

## Results (shipped config: ATR(10), CHOP(14), k=2/3/4 at chop 38/62,
long/short on supertrend flips, exit on the opposite flip, 2xATR stop,
3xATR trail, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 145 | 33.8% | -$1,988 | -19.8% | -1.56 | -28.1% | -$13.71 | 0.74 |
| ETH | 153 | 30.7% | -$1,281 | -13.0% | -0.91 | -21.1% | -$8.38 | 0.83 |
| HYPE | 144 | 36.1% | +$3,379 | +33.9% | +2.06 | -11.9% | +$23.47 | 1.36 |
| **Combined** | **442** | **33.5%** | **+$110** | — | — | — | +$0.25 | — |

Entry gates fire on every coin (BTC 74 long / 73 short flips,
ETH 78 / 77, HYPE 73 / 73).

## Verdict: breakeven on the ledger, and only because HYPE pays

Combined +$110 across 442 trades is a rounding error — expectancy
+$0.25 a trade against ~$8.03 of fees per trade. The pattern is the
familiar batch-36 story: HYPE is the entire green leg (+$3,379,
Sharpe +2.06, PF 1.36, MaxDD only -11.9%), while BTC (-$1,988,
Sharpe -1.56, MaxDD -28.1%) and ETH (-$1,281, Sharpe -0.91) both
bleed. BTC's -28.1% drawdown is the deepest of the three and the
worst expectancy (-$13.71/trade) in the batch so far for a
trend-following flip system.

Two honest mechanics behind the red legs:

- **The hard stop does the exiting, not the flip.** Exit reasons:
  BTC 135 stop / 10 signal, ETH 142 / 11, HYPE 136 / 8. (The
  harness reports both the 2xATR hard stop and the 3xATR chandelier
  trail as "stop".) The flip is mostly a re-entry trigger; positions
  rarely survive long enough for a clean flip exit, which means the
  system is really a 2xATR-stop mean-reversion punching bag on BTC/ETH
  1h chop, not the trend-rider the design intends.
- **The adaptation barely engages.** k=3.0 (the plain default) covers
  76–82% of bars; k=2.0 only 7.5–14.7% and k=4.0 only 7.4–10.5%
  (mean chop ~49–51, i.e. mid-range most of the time). The adaptive
  layer is a thin overlay on a plain Supertrend(10, 3) — and the
  fixed-k sweep in CALIBRATION.md shows plain k=4 (+$524 combined)
  beats the adaptive version (+$110), so the adaptation adds
  complexity without adding edge on this window.

Treat this as a HYPE-only flip filter with a breakeven combined
ledger, not a three-coin strategy.

## Calibration note

Shipped the specified chop thresholds (38/62, Dreiss's published
levels) and k values (2/3/4, the standard Supertrend range) a priori.
The fixed-k sweep is in CALIBRATION.md: k=4 is the in-sample combined
winner (+$524), k=2 is -$681, k=3 is -$2,080, adaptive is +$110. No
setting is switched to on the strength of this window.

## Mechanism

Supertrend (Seban): HL2 ± k·ATR(10) bands with the final-band ratchet
(upper only falls, lower only rises); direction flips on a close
through the opposite final band. Choppiness Index(14) sets k per bar:
chop<38 → 2.0, chop>62 → 4.0, else 3.0. Long on a flip to up, short on
a flip to down; exit on the opposite flip. 2xATR stop, 3xATR trail,
200-bar max hold.

Source: Supertrend (Olivier Seban) —
https://www.investopedia.com/supertrend-indicator-7976167

## Limitations

- Single 7-month crypto window; 442 trades is a thin sample, and the
  combined breakeven depends entirely on HYPE.
- BTC/ETH legs are losers with deep drawdowns; the stop, not the flip,
  is the dominant exit — the trend-following premise does not survive
  contact with 1h BTC/ETH chop.
- The adaptive layer engages on only ~20% of bars; most of the time
  this IS plain Supertrend(10, 3).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped thresholds on this window (see CALIBRATION.md).
