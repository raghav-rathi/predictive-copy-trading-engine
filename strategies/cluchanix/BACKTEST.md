# ClucHAnix — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned window
2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC: BTC/ETH 6,040 bars,
HYPE 6,038 bars.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 6xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=200 bars.

## Results (shipped config: published hyperopt constants, HA +
BB(40, 2σ) pullback entry, Fisher sell exit, 6xATR stop/trail,
72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 2 | 50.0% | +$5 | +0.1% | +0.07 | -1.0% | +$2.72 | 1.24 |
| ETH | 1 | 100.0% | +$62 | +0.6% | +1.64 | -0.4% | +$62.25 | inf |
| HYPE | 7 | 57.1% | +$58 | +0.6% | +0.39 | -1.6% | +$8.26 | 1.33 |
| **Combined** | **10** | **60.0%** | **+$126** | — | — | — | **+$12.55** | — |

Fees: BTC $5, ETH $1, HYPE $9 (total $15).

## Verdict: inconclusive — the sample is far too thin to judge

10 trades across three coins in eight months. The combined
+$126 is a rounding error, and the ETH leg is a single trade.
Nothing here supports or refutes the ClucHAnix thesis:

- This is a 1-minute scalper (the source's KuCoin dry run
  averaged ~50 minutes per trade over 3,080 trades). Ported
  unchanged to 1h bars, its entry pattern — HA close dipping
  below the prior lower band while the band is wide — almost
  never fires: 10 entries in ~18,000 bars. The logic was not
  re-scaled to the new timeframe, and re-scaling it (wider
  bands, looser deltas) on this window would be tuning to the
  backtest, so it stays as published.
- The one structural observation: when it does fire, the
  trades have not blown up — 6 of 10 wins, worst drawdown
  −1.6% — but with 10 trades that is consistent with luck.
- The alternative entry path never fires at the published
  constant (see CALIBRATION.md); effectively all entries come
  from the primary path.

## Mechanism

Heikin Ashi + Bollinger Bands (40, 2σ) on the HA typical price;
primary long entry is a pullback below the prior lower band with
BBDelta/close-delta/tail filters, gated by ROCR(168) > 0.54904;
exit on Fisher > 0.38414 with two lower HA highs and price above
the BB mid; short side is a builder-added mirror. 6xATR stop and
trail (mapping of the source's −15% profit-stepped custom
stoploss), 72-bar max hold. All constants fixed a priori from the
published repo; no optimization.

Source: ssssi/freqtrade_strs — ClucHAnix
(https://deepwiki.com/ssssi/freqtrade_strs/5.2-cluchanix-strategy).

## Limitations

- 10 trades total: no per-coin or combined statistic here is
  significant; do not quote any leg as an edge.
- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Timeframe mismatch is the dominant caveat: a 1m strategy run
  on 1h bars without re-scaling. A real verdict would need the
  strategy run at its native timeframe, or a re-scaling validated
  out-of-sample — not a parameter search on this window.
- Never tune the shipped parameters on this window.
