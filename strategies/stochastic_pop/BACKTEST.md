# Stochastic Pop — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filtered to the task
window t >= 1773446400000 and t <= 1793145600000
(2026-03-14 00:00 UTC → 2026-10-28 00:00 UTC), $10k start, 1%
risk per trade on the 1.5xATR stop, 3x leverage cap, 0.045%
fee + 0.01% slippage per side, funding off. WARMUP=30 bars.

**Actual candle window used (per coin, after filtering):**
the cache's first candle postdates the window's start bound
and the filter caps the end at the bound itself, so the
effective window is narrower than the nominal one:

- BTC: 5,451 bars, first 1773525600000 (2026-03-14 22:00 UTC),
  last 1793145600000 (2026-10-28 00:00 UTC)
- ETH: 5,451 bars, first 1773525600000 (2026-03-14 22:00 UTC),
  last 1793145600000 (2026-10-28 00:00 UTC)
- HYPE: 5,449 bars, first 1773532800000 (2026-03-15 00:00 UTC),
  last 1793145600000 (2026-10-28 00:00 UTC)

Note: `fetch_candles` extended the cache forward during this
run (the cache previously ended 2026-10-27 13:00 UTC). The
unfiltered `scripts/run_strategy_backtest.py` path therefore
includes ~37 extra post-window BTC bars (to Oct 29) and reports
slightly different numbers (BTC 118 trades, -$1,441 vs -$1,396
here); the table below is the filtered-window run and is
authoritative.

## Results (shipped config: fast %K(14) cross of 80/20 with a
same-bar prior-20-bar breakout, 1.5xATR stop, 2xATR trail,
3xATR target, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|
| BTC | 117 | 29.1% | -$1,396 | -1.57 | -18.5% | -$11.93 | 0.69 | $1,678 |
| ETH | 112 | 29.5% | +$132 | +0.21 | -15.4% | +$1.18 | 1.03 | $1,300 |
| HYPE | 144 | 36.8% | -$924 | -1.17 | -15.1% | -$6.42 | 0.80 | $968 |
| **Combined** | **373** | **32.2%** | **-$2,189** | — | — | **-$5.87** | — | **$3,946** |

Exits: 226 signal (pop spent) / 102 stop / 45 target — the
pop exit fires most often, as designed, but the average win
does not cover the churn: fees alone ($3,946) exceed the gross
loss.

## Verdict: loser

-$2,189 across 373 trades. ETH is nominally green (+$132,
PF 1.03, Sharpe +0.21) but that is noise-level, and BTC
(-$1,396, Sharpe -1.57) plus HYPE (-$924) sink the book. A
setup that pays $3,946 in fees to lose $2,189 is churning, not
trading. Do not trade this as shipped.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
