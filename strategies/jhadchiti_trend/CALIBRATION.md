# jhadchiti trend — Calibration

Shipped the author's parameters: 55-bar breakout channel, 30-bar momentum
window, 2xATR(20) stop, 0.75% risk, 2160-bar max hold.

## Sweep: breakout channel ∈ {34, 55, 89} × momentum window ∈ {20, 30, 60}

Same data, funding gate, costs, and risk as BACKTEST.md:

| chan | mom | BTC (tr/net $) | ETH (tr/net $ / win%) | HYPE (tr/net $ / win%) | Combined net $ |
|---|---|---|---|---|---|
| 34 | 20 | 0 / 0 | 66 / +2,472 / 30.3% | 70 / -672 / 27.1% | +1,800 |
| 34 | 30 | 0 / 0 | 72 / +1,659 / 25.0% | 70 / -1,407 / 25.7% | +252 |
| 34 | 60 | 0 / 0 | 63 / +590 / 30.2% | 62 / -1,610 / 25.8% | -1,021 |
| 55 | 20 | 0 / 0 | 60 / +1,096 / 26.7% | 55 / -633 / 29.1% | +463 |
| 55 | 30 | 0 / 0 | 64 / +556 / 23.4% | 55 / -1,268 / 27.3% | -711 |
| 55 | 60 | 0 / 0 | 53 / -18 / 30.2% | 50 / -1,055 / 32.0% | -1,073 |
| 89 | 20 | 0 / 0 | 51 / +536 / 25.5% | 49 / -417 / 28.6% | +120 |
| 89 | 30 | 0 / 0 | 51 / +668 / 27.5% | 48 / -968 / 27.1% | -300 |
| 89 | 60 | 0 / 0 | 48 / -859 / 29.2% | 45 / -874 / 31.1% | -1,733 |

## Verdict: ship the published 55/30

No combination is stable across all tradeable coins: ETH is positive in 7
of 9 (best at 34/20, +$2,472), HYPE is negative in all 9. The author's own
55/30 sits mid-pack. Switching to the best backtested combo (34/20) would
be overfitting to ETH's window — stated plainly, not done. The honest read:
the edge is coin-specific (ETH trend persistence), not parameter-specific.
