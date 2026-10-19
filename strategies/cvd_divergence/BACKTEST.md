# CVD Divergence — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
rows filtered to 1773446400000 <= t < 1792414800000 (2026-03-14 00:00
UTC → 2026-10-19 13:00 UTC; 5,247 bars BTC/ETH, 5,245 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (noted as limitation).
**Sizing:** 1% equity risk per trade on the 4xATR catastrophe stop
(the 3xATR chandelier trailing stop is the real trade manager), 3x
leverage cap, $10k start. WARMUP=100 bars.

## Results (shipped config: close-location CVD, 10-bar price pivots,
60-bar divergence lookback, opposite-divergence exits, 3xATR trailing)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 262 | 42.4% | -$2,501 | -24.9% | -3.53 | -26.2% | -$9.55 | 0.64 |
| ETH | 261 | 43.7% | -$1,713 | -17.1% | -2.21 | -20.5% | -$6.56 | 0.76 |
| HYPE | 240 | 44.2% | -$862 | -8.7% | -1.18 | -14.9% | -$3.59 | 0.86 |
| **Combined** | **763** | **43.4%** | **-$5,076** | — | — | — | -$6.65 | — |

## Verdict: loser, but the least-bad of the three

Win rates (42–44%) look respectable and HYPE is the closest to
breakeven in the whole batch (PF 0.86), but the edge is not there:
every coin loses, Sharpe is negative across the board, and expectancy
is negative on all three. Two structural problems show up in the trade
logs. First, in a sustained decline every bar is a 10-bar pivot low,
so "bullish divergence" fires on nearly every bar of the leg — the
strategy keeps re-entering longs into a falling market, and the 3xATR
trailing stop, while it caps each loss, cannot manufacture an edge.
Second, the volume-delta input is an approximation (see Limitations),
not real buy/sell imbalance.

## Mechanism

Per-bar delta = v × (2c − h − l)/(h − l) (0 when h == l); CVD is its
cumulative sum. A price pivot is a bar whose close is the unique
min/max of the trailing 10-bar window. Bullish regular divergence: at
a pivot low, the nearest earlier pivot low within 60 bars with price
lower and CVD higher → long. Bearish divergence mirrors → short.
Exits: the opposite divergence, or the 3xATR chandelier trailing stop
managed by the harness (a 4xATR hard stop exists only for sizing).

Source: TradingView "Cumulative Volume Delta with Divergence"
(zjvhcYEe) —
https://fr.tradingview.com/script/zjvhcYEe-Cumulative-Volume-Delta-with-Divergence/

## Limitations

- **The volume delta is an approximation, stated honestly:** Hyperliquid
  1h candles do not publish tick-level buy/sell volume, so delta is
  estimated from where the close sits inside the bar's range. A bar
  that closes near its high is scored as net buying regardless of how
  the volume actually printed. This is the standard TradingView-CVD
  approximation, not measured order flow.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution.
- Consecutive-bar pivots in straight legs make the divergence fire
  repeatedly into the same move (documented in CALIBRATION.md via the
  pivot-window sweep).
- No minimum separation between the compared pivots; the nearest
  earlier pivot inside 60 bars is used.
