# Gann swing (1-bar / 3-bar) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 1-bar minor swing + 3-bar main trend, pullback
entries with the trend, exits on trend flip, 2xATR stop, no trail,
96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 605 | 25.0% | −$7,461 | −74.3% | −7.91 | −75.3% | −$12.33 | 0.46 |
| ETH | 584 | 25.9% | −$6,164 | −59.8% | −4.64 | −62.1% | −$10.55 | 0.58 |
| HYPE | 544 | 35.0% | −$2,328 | −23.3% | −1.46 | −27.3% | −$4.28 | 0.85 |
| **Combined** | **1,733** | **28.4%** | **−$15,953** | — | — | — | **−$9.20** | — |

## Verdict: decisive loser — do not ship, do not tune further

1,733 trades and negative everywhere: the 1-bar swing turns too often
inside hourly chop, so "pullback entries with the trend" become
fade-the-noise entries against it. BTC's −74.3% / Sharpe −7.91 is a
blowup, not a drawdown. The mechanism is faithfully implemented (the
crafted-series unit test proves the pullback entry fires exactly as
specified) — the idea itself does not survive 1h crypto. Reported as
built and rejected, per the honest-loser rule.

## Implementation notes (rules in my own words)

- 1-bar swing: up when the bar makes both a higher high and a higher
  low than the prior bar; down on lower high + lower low; inside and
  outside bars hold the prior swing direction.
- 3-bar main trend: flips up on a break of the prior 3-bar high, down
  on a break of the prior 3-bar low; otherwise holds (an outside bar
  breaking both keeps the prior trend).
- Entry: main trend up + 1-bar swing turning up after being down
  (pullback timing); mirror for shorts. Exits on main-trend flip.
