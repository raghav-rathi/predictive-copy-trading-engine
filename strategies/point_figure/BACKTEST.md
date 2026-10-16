# Point & Figure 3-box reversal — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: box = 0.5xATR(14), 3-box reversals, entries on
double-top / double-bottom breaks of >= 1 box, exit on the opposite
breakout, 2xATR stop, no trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 95 | 17.9% | +$1,019 | +10.8% | +0.72 | −20.2% | +$10.72 | 1.12 |
| ETH | 90 | 17.8% | +$355 | +8.7% | +0.61 | −20.1% | +$3.94 | 1.05 |
| HYPE | 83 | 30.1% | +$704 | +13.1% | +0.88 | −12.1% | +$8.48 | 1.11 |
| **Combined** | **268** | **21.6%** | **+$2,078** | — | — | — | **+$7.76** | — |

## Verdict: the batch's only clean winner — green on all three coins

The classic breakout logic holds up: low win rates (18–30%, normal for
breakout systems) with profit factors just above 1.0 on every coin.
HYPE is the best risk-adjusted print (Sharpe +0.88, −12.1% max DD);
BTC contributes the most dollars. The −20% drawdowns on the majors show
the failure mode plainly — whipsaw reversals in chop — but the trend-leg
captures more than pay for it. Honest caveat: profit factors of
1.05–1.12 are thin; this is a working edge, not a strong one, and it
wants walk-forward validation before any capital.

## Implementation notes (rules in my own words)

- Box = 0.5 * ATR(14) per bar; columns built causally from closes; a
  column reverses after a 3-box move against it; the new column is drawn
  starting 1 box back from the old extreme.
- Double-top buy: the active X column's top crosses >= 1 box above the
  previous X column's top. Double-bottom sell: mirror. Signals use only
  P&F state through bar i's close, executed at bar i+1's open.
