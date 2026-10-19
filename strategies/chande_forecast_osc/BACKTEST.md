# Chande Forecast Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
rows filtered to 1773446400000 <= t < 1792414800000 (2026-03-14 00:00
UTC → 2026-10-19 13:00 UTC; 5,247 bars BTC/ETH, 5,245 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (noted as limitation).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage
cap, $10k start. WARMUP=40 bars.

## Results (shipped config: TSF n=20 one-step-ahead OLS forecast,
FO = (close − forecast)/close×100, 3-bar SMA signal, cross entries
with FO sign gate, cross-back exits, 2xATR stop, 40-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 922 | 29.9% | -$7,109 | -71.1% | -9.08 | -72.2% | -$7.71 | 0.57 |
| ETH | 891 | 32.7% | -$5,511 | -55.1% | -5.58 | -56.1% | -$6.19 | 0.66 |
| HYPE | 1,019 | 34.8% | -$5,941 | -59.4% | -7.36 | -59.6% | -$5.83 | 0.62 |
| **Combined** | **2,832** | **32.6%** | **-$18,561** | — | — | — | -$6.55 | — |

## Verdict: the worst of the three — structurally an overtrader

This is the clearest failure in the batch. The oscillator crosses its
own 3-bar signal line almost constantly in chop — 922 to 1,019 trades
per coin over 5,247 bars, roughly one round-trip every 5 bars — and
every flip pays the 0.055%/side toll ($15,659 in fees combined, nearly
matching the gross loss). The exits (cross back through the signal)
fire just as fast as the entries, so no position ever survives long
enough to pay for the whipsaw: max hold is 40 bars but the median
holding time is a handful of bars. Win rates near 30–35% with PF
0.57–0.66 and Sharpe −5.6 to −9.1 leave no ambiguity. The FO>0/FO<0
sign gate also makes the strategy lopsided — on this window it found
far more short setups than longs — but removing the gate would only
add more churn, not edge.

## Mechanism

TSF: for each bar i ≥ 20, an OLS line fit on closes[i−20..i−1],
extrapolated one step ahead = the forecast made at bar i−1 for bar i
(vectorized, exactly np.polyfit per window). FO = (close −
forecast_prev)/close × 100; signal = 3-bar SMA of FO. Long when FO
crosses above the signal with FO > 0; short when FO crosses below with
FO < 0; exit on the cross back. 2xATR hard stop, no trailing/target,
40-bar max hold.

Source: MQL5 CodeBase 21827 (Chande Forecast Oscillator) —
https://www.mql5.com/en/code/21827

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution.
- The 3-bar signal line is so fast that entry and exit crosses fire
  on microstructure noise — the strategy as specified is a churn
  machine; CALIBRATION.md shows longer TSF windows do not fix it.
- No volatility filter or minimum-hold: positions routinely exit
  within a few bars of entry.
- The sign gate (FO>0 for longs) suppresses most long setups on this
  window; the short side dominates the trade count.
