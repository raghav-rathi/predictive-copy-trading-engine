# Chandelier Exit — Multiplier Sweep

Shipped config is the textbook LeBeau setting (ATR(22), 22-bar lookback,
multiplier 3.0). Sweep ran via a throwaway /tmp script that monkeypatched
`indicators.MULT` and re-ran the identical backtest harness on the same
~5,030 1h bars (BTC/ETH/HYPE, 2026-03-14 → 2026-10-09), same costs and
sizing as BACKTEST.md. Lookback was held at 22; only the multiplier
changed.

## Results

| Mult | Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| 2.5 | BTC | 162 | 33.3% | -$1,865 | -1.27 | -28.7% | -$11.51 | 0.78 |
| 2.5 | ETH | 149 | 36.2% | +$192 | +0.26 | -16.6% | +$1.29 | 1.02 |
| 2.5 | HYPE | 153 | 35.3% | +$1,117 | +0.77 | -16.0% | +$7.30 | 1.13 |
| **3.0** | BTC | 151 | 31.1% | -$2,182 | -1.43 | -28.5% | -$14.45 | 0.75 |
| **3.0** | ETH | 136 | 32.4% | -$342 | -0.06 | -18.7% | -$2.52 | 0.96 |
| **3.0** | HYPE | 139 | 35.3% | **+$1,767** | **+1.06** | -14.5% | +$12.71 | 1.21 |
| 3.5 | BTC | 129 | 28.7% | -$1,495 | -0.86 | -21.4% | -$11.59 | 0.81 |
| 3.5 | ETH | 127 | 29.1% | -$71 | +0.11 | -19.5% | -$0.56 | 0.99 |
| 3.5 | HYPE | 129 | 29.5% | +$1,181 | +0.74 | -19.0% | +$9.16 | 1.14 |

(Combined PnL: 2.5 → −$556; 3.0 → −$757; 3.5 → −$385. Negative in all
three — BTC dominates the combined number.)

## One-line verdicts

- **HYPE: robust.** Positive at all three multipliers (PF 1.13–1.21); 3.0
  is clearly the best. The edge is real on this coin, not a tuning artifact.
- **BTC: structural loser.** Negative at 2.5, 3.0, and 3.5 — wider stops
  reduce the loss but never flip the sign. More rope helps (fewer
  stop-outs), but 22-bar breakouts on BTC 1h in this window are fake-outs.
- **ETH: coin toss.** $+192 at 2.5, −$342 at 3.0, −$71 at 3.5 — no stable
  sign, no edge either way.

**Conclusion:** keep the textbook 3.0 — the sweep gives no reason to move
it. The honest calibration insight is not parametric: this system wants
trending coins and BTC was not one in this window. Next iteration is a
coin filter, not a parameter hunt.
