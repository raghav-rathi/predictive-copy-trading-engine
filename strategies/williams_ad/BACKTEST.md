# Williams Accumulation/Distribution — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
rows filtered to 1773446400000 <= t < 1792414800000 (2026-03-14 00:00
UTC → 2026-10-19 13:00 UTC; 5,247 bars BTC/ETH, 5,245 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (noted as limitation).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: WAD SMA 20, price SMA 50, cross-with-trend
entries, cross-back exits, 2xATR stop, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 393 | 19.3% | -$4,359 | -42.8% | -2.96 | -50.2% | -$11.09 | 0.60 |
| ETH | 386 | 16.8% | -$3,512 | -35.1% | -2.05 | -41.6% | -$9.10 | 0.71 |
| HYPE | 354 | 23.2% | -$2,490 | -24.9% | -2.04 | -29.6% | -$7.03 | 0.75 |
| **Combined** | **1,133** | **19.7%** | **-$10,361** | — | — | — | -$9.15 | — |

## Verdict: loser on all three coins

A clean, honest loss. The mechanism trades accumulation *confirmation*
(WAD crossing above its SMA in an uptrend), but on 1h crypto the WAD
cross fires late: by the time the cumulative pressure series turns,
the move is mostly done, and the cross-back exit fires just as late on
the way down. Win rates of 17–23% are trend-follower territory, but
the winners are not large enough to pay for the whipsaw — profit
factor 0.60–0.75 everywhere, Sharpe negative on all three. Fees
($7,394 combined) are material but the gross edge is absent too.
There is no coin split to hide behind: it fails on BTC, ETH, and
HYPE alike.

## Mechanism

WAD is built bar by bar from the cTrader definition: if close >
prev_close, add (close − min(prev_close, low)); if close < prev_close,
add (close − max(prev_close, high)); else add nothing. Long entries
when close > 50-bar SMA of price AND WAD crosses above its 20-bar SMA;
shorts mirror. Exits on the cross back through the WAD SMA. 2xATR hard
stop, no trailing/target (the cross-back manages the trade), 60-bar
max hold.

Source: cTrader built-in indicator docs (Larry Williams A/D) —
https://help.ctrader.com/indicators/built-in/other/williams-accumulation-distribution/

## Limitations

- Single 7-month crypto window; no bull-market or multi-year sample.
- Funding unmodeled.
- Next-bar-open execution vs idealized signal-bar entry.
- The WAD SMA cross is inherently lagging on both entry and exit;
  CALIBRATION.md shows the lag shortens with a faster SMA but the
  whipsaw gets worse, not better.
- 50-bar price-SMA warmup excludes the first ~80 bars from trading.
