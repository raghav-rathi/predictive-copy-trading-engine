# raschke_tail — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: tail bar = wick >= 2x body, wick >= 50% of
range, fresh 20-bar extreme, range >= 0.75x ATR; buy/sell-stop entry
within 3 bars; 2xATR stop, 3xATR trail, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 134 | 37.3% | −$1,814 | −18.1% | −1.67 | −23.7% | −$13.54 | 0.74 |
| ETH | 125 | 36.0% | −$592 | −5.9% | −0.36 | −20.8% | −$4.74 | 0.92 |
| HYPE | 110 | 36.4% | −$591 | −5.9% | −0.43 | −17.4% | −$5.37 | 0.90 |
| **Combined** | **369** | **36.6%** | **−$2,997** | — | — | — | **−$8.12** | — |

## Verdict: honest loser on all three coins

The Tail pattern does not survive hourly crypto. BTC is the worst
(−18.1%, Sharpe −1.67): the 2026 down-drift means "fresh 20-bar low"
tails keep printing into a falling knife, and the buy-stop above the
tail bar fills on dead-cat bounces that roll over into the 2xATR stop.
ETH/HYPE are smaller losers (−5.9% each) — the 3xATR trail can't save a
sub-40% win rate with a 0.9 profit factor. The calibration sweep shows
a stricter wick (2.5x) trims losses but never flips a coin positive.
No variant is promotable; this one stays in the library as a documented
loser.
