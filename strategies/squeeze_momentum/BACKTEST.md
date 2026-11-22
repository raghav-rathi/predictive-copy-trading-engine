# LazyBear Squeeze Momentum — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: BTC/ETH 6,040 bars, HYPE 6,038 bars,
2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR(14) stop, 3x
leverage cap, $10k start, long/short. WARMUP=110 bars.

## Results (shipped config: squeeze release + rising positive
linear-regression momentum at its 100-bar low + close above
EMA(100) and above the prior close; exit on the first momentum
downtick; 2xATR(14) stop; 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 0 | — | $0 | 0.0% | 0.00 | 0.0% | — | — |
| ETH | 0 | — | $0 | 0.0% | 0.00 | 0.0% | — | — |
| HYPE | 0 | — | $0 | 0.0% | 0.00 | 0.0% | — | — |
| **Combined** | **0** | — | **$0** | — | — | — | — | — |

Fees: $0 total.

## Verdict: no verdict possible — the strategy never traded

Zero trades on all three coins, so there is nothing to score.
The entry gate, not the market, is the cause. Diagnostic on
the pinned window:

| Coin | Squeeze bars | Releases | Release + rising & positive mom | + 100-bar mom extreme | Full entry |
|---|---|---|---|---|---|
| BTC | 1,124 | 162 | 75 | 0 | 0 |
| ETH | 1,368 | 167 | 82 | 0 | 0 |
| HYPE | 843 | 133 | 58 | 0 | 0 |

The squeeze/release core works fine — 133–167 releases per
coin, and 58–82 of them have rising positive momentum. The
100-bar momentum-extreme gate kills every single one: **zero**
releases on any coin have momentum at its trailing-100-bar low
(long) or high (short). As literally specified, the gate is
nearly self-contradictory: a rising, positive momentum value is
almost never simultaneously the lowest momentum value of the
last 100 bars (the 100-bar minimum was set during the flat
squeeze itself, when momentum hovered near or below zero, and
the release pushes momentum up away from it). The short mirror
fails identically.

Stated plainly: the published rule, implemented literally,
does not trade on 1h crypto in this window. That is a finding
about the rule as written — not evidence for or against the
squeeze-momentum thesis, which the existing `ttm_squeeze` /
`bollinger_keltner_squeeze` strategies (same release core
without the 100-bar-extreme gate) already cover. The gate was
NOT relaxed to manufacture trades: loosening it until entries
appear would be tuning the entry to this window. If the rule is
revisited, the question to answer first — from the Pine source,
not from this window — is what "at a local low" was meant to
compare against (e.g. the momentum extreme over a lookback
ending before the release bar, rather than including it).

## Mechanism

Squeeze = BB(20, 2σ) inside KC(20 EMA, 1.5×ATR(14)); entry on
the release bar when the linear-regression momentum is rising
and positive, at its trailing-100-bar low, with close above
EMA(100) and above the prior close; mirror for shorts. Exit on
the first momentum downtick (long) / uptick (short); 2xATR(14)
stop added as a backstop (the source specifies none). All
params fixed a priori; no optimization. Deviations (8%-of-equity
sizing → 1% risk sizing, stop added, KC ATR window) are
documented in CALIBRATION.md.

Source: TradingView — Squeeze Momentum Indicator Strategy
[LazyBear + PineIndicators]
(https://th.tradingview.com/script/G40dtEbK-Squeeze-Momentum-Indicator-Strategy-LazyBear-PineIndicators/).

## Limitations

- Zero trades: every statistic is undefined; do not quote any
  per-coin number as a result.
- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
