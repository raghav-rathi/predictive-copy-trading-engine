# TD Sequential — Backtest

Strategy: Tom DeMark Sequential — 9-bar setup + 13-bar countdown with perfection
filter and TDST support/resistance exits; 1.5xATR disaster stop, 96-bar max hold
(risk overlays calibrated — see CALIBRATION.md; the perfection filter itself is
the published classic default).

Source: Tom DeMark, *The New Science of Technical Analysis* (Wiley 1994);
mechanics ref https://www.litefinance.org/blog/for-professionals/technical-analysis-tool-by-tom-demark-td-sequential/

## Config

- Data: Hyperliquid 1h candles, cached offline (`strategies/data.py`
  `fetch_candles(..., use_cache=True)`), **2026-03-14 → 2026-10-13**
  (BTC/ETH 5104 bars, HYPE 5102 bars)
- start_equity=$10,000, risk_frac=0.01, max_leverage=3.0,
  fee_rate=0.00045, slippage_rate=0.0001, use_funding=False, warmup=30 bars
- Entry: bar completing a perfected + qualified countdown, filled at next open
  (harness convention; the published rule enters at the signal bar's close)
- Paper only. No live execution.

## Results (shipped config: stop 1.5xATR, max hold 96 bars)

| coin | net PnL $ | trades | win rate % | Sharpe | max DD % | expectancy $/trade |
|------|-----------|--------|------------|--------|----------|--------------------|
| BTC  | +1590.13  | 17     | 35.3       | 1.87   | -6.43    | +93.54             |
| ETH  | +4076.45  | 17     | 41.2       | 2.80   | -5.50    | +239.79            |
| HYPE | -179.13   | 25     | 28.0       | -0.22  | -9.48    | -7.17              |

Exit mix: BTC 8 stop / 8 signal / 1 max_hold; ETH 10 signal / 6 stop / 1 max_hold;
HYPE 12 signal / 11 stop / 2 max_hold.

## Honest read

- Trade counts are low (17–25 over ~7 months) — expected for TD Sequential;
  countdown completions are rare events. Do not expect this to scale to
  high-frequency sizing.
- ETH is the clear winner (+40.8% on equity, Sharpe 2.80, profit factor 4.99);
  BTC solid (+15.9%, Sharpe 1.87); **HYPE is still a loser** (-$179, Sharpe
  -0.22, win rate 28%) — the countdown reversal pattern does not pay on HYPE's
  trend regime in this window, though calibration cut the loss by two-thirds.
- The disaster stop did real work (25 stop-outs across coins); TDST/opposite-
  countdown signal exits carried most ETH winners.
