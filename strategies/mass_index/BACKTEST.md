# Mass Index — Backtest

Strategy: Donald Dorsey's Mass Index (S&C, June 1992) — MI = 25-bar sum of
EMA(High-Low,9)/EMA(EMA(High-Low,9),9); reversal bulge = MI above 27 then back
below 26.5. **Direction is OUR extension** (the published indicator is
directionless): long on bulge completion if close < SMA(20), short if close >
SMA(20). Exits: 3xATR trailing stop, opposite bulge, 2xATR disaster stop.

Source: https://www.gate.com/crypto-wiki/article/what-is-mass-index-a-comprehensive-guide-to-crypto-reversal-signals-20260116

## Config

- Data: Hyperliquid 1h candles, cached offline (`strategies/data.py`
  `fetch_candles(..., use_cache=True)`), **2026-03-14 → 2026-10-13**
  (BTC/ETH 5104 bars, HYPE 5102 bars)
- start_equity=$10,000, risk_frac=0.01, max_leverage=3.0,
  fee_rate=0.00045, slippage_rate=0.0001, use_funding=False, warmup=80 bars
- Paper only. No live execution.

## Results

| coin | net PnL $ | trades | win rate % | Sharpe | max DD % | expectancy $/trade |
|------|-----------|--------|------------|--------|----------|--------------------|
| BTC  | -927.30   | 35     | 34.3       | -1.45  | -11.98   | -26.49             |
| ETH  | +1882.41  | 35     | 45.7       | 2.06   | -4.61    | +53.78             |
| HYPE | +156.75   | 23     | 39.1       | 0.36   | -5.41    | +6.82              |

Exit mix: BTC 35 stop; ETH 33 stop / 2 max_hold; HYPE 22 stop / 1 signal.

## Honest read

- **BTC is a clear loser** (-$927, -9.3% on equity, max DD -12%, profit factor
  0.53): all 35 trades exited via stops — the snap-back either doesn't happen
  on BTC or the 3xATR trail gives back too much.
- **ETH is a solid winner** (+$1882, +18.8%, Sharpe 2.06, PF 2.05) on the same
  35 trades — the SMA(20) direction extension works on ETH's regime, not BTC's.
- HYPE is noise (+$157, Sharpe 0.36).
- The direction rule is ours, not Dorsey's — the mixed coin results say the
  extension is regime-dependent, not a general edge. Do not run this on BTC.
