# EMA/VWAP Breakout-Retest (@EllyDtrades) — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk on 2xATR disaster stop, 48-bar max hold, $10k start.
**Source:** https://threadreaderapp.com/thread/1857227985428087014.html

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 168 | 18.5% | -$3,589 (-35.9%) | -5.62 | -38.9% | -$21.36 | 0.34 |
| ETH | 151 | 16.6% | -$1,312 (-13.1%) | -1.05 | -25.3% | -$8.69 | 0.77 |
| **Combined** | **319** | — | **-$4,902** | — | — | — | — |

## Diagnosis: timeframe-port failure

146 of 168 BTC exits are the 8-EMA trailing exit; average hold is 4.3 hours.
Elly's system is built for **10-minute equity charts** — the 8 EMA is a
tight intraday trailer that works when trends are smooth. Ported to 1h
crypto bars, normal noise tags the 8 EMA constantly: 18% win rate, exits
fire before any move develops.

The mechanics are faithfully implemented (trend stack + breakout memory +
retest trigger all verified in unit tests); the system itself isn't
disproven — the *port* is. A faithful crypto port would need 10-15m bars,
which this 1h dataset can't test.

## Verdict: LOSER as ported

Do not run this on 1h bars. If revisited, rebuild on 15m candles with the
same rules before judging the system itself.
