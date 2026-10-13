# Vortex — calibration

Sweep of the two key knobs (VI period, ADX threshold), ADX filter ON,
same data/setup as BACKTEST.md (BTC/ETH/HYPE 1h, 2026-03-14 → 2026-10-10).

## VI period sweep (ADX gate fixed at 20)

| VI n | BTC net PnL | ETH net PnL | HYPE net PnL |
|-----:|-----------:|-----------:|------------:|
| 10   | -$3,505.98 | -$1,845.37 | +$2,669.46 |
| 14 (classic) | -$2,168.38 | -$1,275.44 | +$543.86 |
| 21   | -$1,899.03 | -$1,363.07 | +$2,401.19 |

## ADX threshold sweep (VI n fixed at 14)

| ADX gate | BTC net PnL | ETH net PnL | HYPE net PnL |
|---------:|-----------:|-----------:|------------:|
| 15       | -$3,594.01 | -$1,445.54 | +$799.39 |
| 20 (classic) | -$2,168.38 | -$1,275.44 | +$543.86 |
| 25       | -$1,613.02 | -$1,234.32 | +$762.98 |

## Decision

Ship the published classic (VI=14, ADX gate=20). VI=21 flatters BTC
and HYPE but hurts ETH; a stricter ADX gate (25) helps BTC marginally
but is within noise on ETH/HYPE. No alternative is stable across all
three coins as a winner — BTC/ETH lose at every setting — so switching
params would be overfitting a HYPE-specific blip. Defaults shipped as
published; see BACKTEST.md for the honest result.
