# Holy Grail — Backtest

Strategy: Linda Raschke & Larry Connors "Holy Grail" (Street Smarts, Ch.10) —
ADX(14) > 30 and rising, first pullback touching the 20 EMA, buy stop above the
touch bar's high, protective stop at the newly formed swing low; one signal per
ADX turn-up; exit on swing-low close or ADX < 25.

Source: https://medium.com/mudrex/the-holy-grail-trading-strategy-1668bacf99a2

## Config

- Data: Hyperliquid 1h candles, cached offline (`strategies/data.py`
  `fetch_candles(..., use_cache=True)`), **2026-03-14 → 2026-10-13**
  (BTC/ETH 5104 bars, HYPE 5102 bars)
- start_equity=$10,000, risk_frac=0.01, max_leverage=3.0,
  fee_rate=0.00045, slippage_rate=0.0001, use_funding=False, warmup=60 bars
- The ADX gate was NOT diluted: ADX > 30 and rising, strictly.
- Timing approximation: the touch bar is identified at its close and the
  breakout on the breakout bar's high, so the harness fills at the next bar's
  open — one bar later than a true buy-stop fill.
- Paper only. No live execution.

## Results

| coin | net PnL $ | trades | win rate % | Sharpe | max DD % | expectancy $/trade |
|------|-----------|--------|------------|--------|----------|--------------------|
| BTC  | -441.40   | 4      | 0.0        | -2.89  | -4.47    | -110.35            |
| ETH  | -158.53   | 2      | 0.0        | -2.09  | -1.61    | -79.27             |
| HYPE | +761.04   | 5      | 60.0       | 1.87   | -2.60    | +152.21            |

Exit mix: BTC 4 stop; ETH 1 stop / 1 signal; HYPE 5 signal.

## Honest read

- **The published setup barely fires on 1h crypto in this window: 11 trades
  total across 3 coins over 7 months.** The ADX>30-and-rising + first-pullback
  conjunction is rare; I did not loosen it.
- BTC and ETH are losers (0% win rate — every trade stopped out). HYPE is a
  winner (+$761, 60% win, profit factor 7.14) but on 5 trades, which is noise
  territory.
- Verdict: as a literal published-rules system on 1h perps, this does not earn
  a slot — too few trades to be statistically meaningful, and negative where it
  did trade on the majors. The HYPE print is interesting but not evidence.
