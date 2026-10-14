# Wilder DMI/ADX + Parabolic SAR — Backtest

Strategy: J. Welles Wilder, *New Concepts in Technical Trading Systems* (1978) —
+DI(14)/-DI(14) cross with ADX(14) > 25 and rising for entries; exits on
Parabolic SAR flip, ADX < 20, or Wilder's range rule (ADX below both DI lines).

Source: https://dev.to/mt5depot/adx-trend-filter-in-an-mt5-ea-wiring-it-from-blocks-and-where-it-breaks-27af

## Config

- Data: Hyperliquid 1h candles, cached offline (`strategies/data.py`
  `fetch_candles(..., use_cache=True)`), **2026-03-14 → 2026-10-13**
  (BTC/ETH 5104 bars, HYPE 5102 bars)
- start_equity=$10,000, risk_frac=0.01, max_leverage=3.0,
  fee_rate=0.00045, slippage_rate=0.0001, use_funding=False, warmup=60 bars
- Paper only. No live execution.

## Results

| coin | net PnL $ | trades | win rate % | Sharpe | max DD % | expectancy $/trade |
|------|-----------|--------|------------|--------|----------|--------------------|
| BTC  | -119.80   | 3      | 33.3       | -1.25  | -2.17    | -39.93             |
| ETH  | -104.81   | 1      | 0.0        | -2.13  | -1.05    | -104.81            |
| HYPE | +910.72   | 4      | 75.0       | 3.14   | -1.46    | +227.68            |

Exit mix: BTC 3 signal; ETH 1 stop; HYPE 3 signal / 1 stop.

## Honest read

- **8 trades total across 3 coins over 7 months.** The DI-cross + ADX>25 +
  rising conjunction almost never fires on 1h crypto — the gate is doing what
  Wilder designed it to do (keep you out), but there is no tradable frequency here.
- HYPE prints +$911 at 75% win / Sharpe 3.14, but that is 4 trades — noise,
  not an edge. BTC/ETH are small losers.
- Verdict: not a viable standalone system on 1h perps in this window; the
  signal is too rare to evaluate or size. Kept as a research-grade
  implementation of the published rules.
