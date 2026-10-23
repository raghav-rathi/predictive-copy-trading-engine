# Pin Bar Reversal — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), sliced to `[1773446400000, 1792713599000)` (2026-03-14 00:00
UTC → 2026-10-22 23:59 UTC): 5,330 bars BTC/ETH, 5,328 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1xATR stop, 3x leverage
cap, $10k start, both sides. WARMUP=40 bars.

## Results (shipped config — fixed a priori, no sweep)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 193 | 36.8% | -$3,378 | -33.8% | -2.47 | -36.8% | -$17.50 | 0.73 |
| ETH | 199 | 33.2% | -$3,927 | -39.3% | -3.01 | -42.1% | -$19.73 | 0.68 |
| HYPE | 187 | 35.8% | -$3,073 | -30.7% | -2.23 | -30.8% | -$16.43 | 0.75 |
| **Combined** | **579** | **35.2%** | **-$10,378** | — | — | — | -$17.92 | **0.72** |

Fees: BTC $3,535, ETH $2,715, HYPE $1,653 (combined $7,902).

## Verdict: loser — the pattern does not survive the 1h crypto tape

This is a clean red across all three coins: PF 0.68–0.75, Sharpe
-2.2 to -3.0, expectancy -$16 to -$20 per trade. It is not a
fee-noise story either — gross losses exceed gross wins by a wide
margin before costs.

Why the textbook pattern fails here:

- **A 1h pin tail is usually continuation, not absorption.** On
  crypto 1h bars, a violent wick down at a "swing low" is far more
  often a stop-hunt in a fresh leg down than committed buying — the
  next bar continues the flush and the 1xATR stop eats the trade.
  The canon was calibrated on daily equities/forex, where a
  rejection tail prints over 24 hours of diverse flow.
- **The 5-bar swing filter is too shallow.** On 1h crypto, a
  5-bar extreme is intraday noise, not a structural level — so the
  "location" requirement admits exactly the stop-hunt bars the
  pattern is meant to avoid.
- **Win rate 35% at 2R can't pay.** The strategy needs ~36%+ wins
  just to break even at 1:2; it lands at 33–37% with the losers
  arriving at full stop size.

The honest read: a faithful implementation of a genuine
price-action pattern, empirically rejected on this window. Ship as
a documented loser — the negative result is the finding.

## Mechanism

`bullish_pin = (lower_wick >= 2/3·rng) & (body <= 1/3·rng) &
(upper_wick <= 0.2·rng) & (l == 5-bar rolling min)`,
bearish mirror. Long on bullish pin, short on bearish pin, exit on
the opposite rejection. 1xATR stop, 2xATR target, 48-bar max hold.

Sources: https://halleytech.substack.com/p/reversal-candlestick-patterns —
https://quantstrategy.io/blog/what-is-pin-bar-pin-bar-reversal-trading-strategies/

## Limitations

- Single 7-month crypto window; 579 trades is a decent sample but
  one regime.
- 1h timeframe only — the pattern may behave differently on daily
  bars (untested, out of scope).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
