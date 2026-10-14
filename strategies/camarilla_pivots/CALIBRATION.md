# Camarilla pivots — calibration

Variant sweep (mode x session definition), same data/setup as
BACKTEST.md (BTC/ETH/HYPE 1h, 2026-03-14 → 2026-10-10). Net PnL:

| Variant            | BTC       | ETH       | HYPE      |
|--------------------|----------:|----------:|----------:|
| fade / utc         | -$1,009.91 | -$2,183.49 | -$1,129.99 |
| fade / rolling     | -$2,637.06 | -$1,712.15 |   -$660.63 |
| breakout / utc     | -$1,296.10 |    +$50.26 |   +$584.84 |
| breakout / rolling | +$2,022.97 |   +$468.83 | +$1,294.81 |

## Decision

Ship fade + UTC session as the default — that is the published Nick
Stott method (levels from the prior full session, fade the extremes).

Session definition: UTC wins for fade (rolling is materially worse on
BTC/ETH); rolling wins for breakout. This is reported as found, not
tuned away.

Mode: fade loses on all three coins; breakout/rolling is positive on
all three — but on 47/47/24 trades, which is too thin to promote it to
the default or to claim stability. Stated plainly: the only
consistently positive variant is breakout/rolling, and it needs
out-of-sample validation before anyone trusts it. Fade stays the
default per the published method; BACKTEST.md carries the honest
numbers.
