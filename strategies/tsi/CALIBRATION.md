# TSI — calibration

Parameter sweep, zero gate ON, exhaustion OFF, same data/setup as
BACKTEST.md (BTC/ETH/HYPE 1h, 2026-03-14 → 2026-10-10). Net PnL:

| (r, s)         | BTC       | ETH       | HYPE      |
|----------------|----------:|----------:|----------:|
| (25, 13) classic | -$3,644.57 | -$2,811.69 | +$4,303.92 |
| (20, 10)       | -$3,743.65 | -$3,151.84 | +$2,510.75 |
| (30, 15)       | -$3,248.79 | -$2,120.70 | +$4,700.99 |

| Variant            | BTC       | ETH       | HYPE      |
|--------------------|----------:|----------:|----------:|
| zero gate ON       | -$3,644.57 | -$2,811.69 | +$4,303.92 |
| zero gate OFF      | -$4,643.98 | -$3,990.60 | +$2,116.64 |
| exhaustion ON      | -$3,425.80 | -$2,205.59 | +$2,183.77 |

## Decision

Ship Blau's published classic (25, 13, signal 7) with the zero-line
gate ON and exhaustion OFF. The (30,15) pair beats the classic on all
three coins in this window, but the strategy still loses on BTC/ETH at
every setting — switching params would be fitting a slower filter to a
loser, not finding a stable winner. The only stable signal in the
sweep is structural, not parametric: the zero-line gate helps on all
three coins (fewer, better trades), and exhaustion exits stay off
because they cost more on HYPE than they save on BTC/ETH. Stated
plainly: defaults shipped as published; (30,15) noted as a candidate
for future out-of-sample testing, not adopted.
