# Kalman Filter Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,271 bars BTC/ETH, 5,269 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=40 bars.

## Results (shipped config: 1-D Kalman filter, price+velocity state,
Q=diag(0.05,0.01), R=1.0; long on close-cross-above-kf with kf_slope>0,
short on the mirror; exits on the opposite cross; 2xATR stop, 200-bar
max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1,056 | 26.9% | -$7,472 | -74.7% | -7.92 | -76.2% | -$7.08 | 0.59 |
| ETH | 978 | 28.0% | -$6,306 | -63.1% | -5.69 | -65.8% | -$6.45 | 0.66 |
| HYPE | 1,068 | 31.1% | -$6,168 | -61.6% | -6.57 | -63.2% | -$5.78 | 0.65 |
| **Combined** | **3,102** | **28.7%** | **-$19,946** | — | — | — | -$6.43 | — |

## Verdict: loser — whipsawed to death by its own zero-lag filter

The strategy loses on all three coins, and the sample is large enough
(3,102 trades) that this is a robust negative, not noise. The failure
mode is structural: the velocity-state Kalman filter tracks a steady
drift with essentially zero steady-state lag (measured: |c - kf| ≈
5.7e-14 on a linear rally), so in choppy 1h markets the close crosses
the filter constantly — ~1,000 entries per coin over 5,271 bars, an
entry roughly every 5 bars. Each touch-and-go cross fires a 1–2 bar
trade that pays 0.045% + 0.01% per side and then exits on the reverse
cross. Fees are the dominant story: $6,986 of BTC's $7,472 loss,
$5,977 of ETH's $6,306, $3,347 of HYPE's $6,168 — the gross edge is
roughly zero and costs do the rest. Win rates sit at 27–31% with profit
factors of 0.59–0.66: the filter is always "right" about where price
just was, and always late about where it is going. The slope
confirmation does not save it — in chop the filter wiggles enough that
the slope condition is satisfied on most crosses.

## Calibration note

Shipped the specified R=1.0. An r ∈ {0.5, 1.0, 2.0} sweep is in
CALIBRATION.md: every setting loses on every coin; r=2.0 bleeds
slowest (fewer trades → less fee drag) and r=0.5 bleeds fastest. There
is no in-sample winner, so nothing was adopted — r=1.0 stays as
specified. The knob moves the loss, it does not flip the sign.

## Mechanism

1-D Kalman filter on hourly closes with state x = [price, velocity]:
F = [[1,1],[0,1]], H = [1,0], Q = diag(0.05, 0.01), R = 1.0; init
x = [first close, 0], P = diag(1, 1). Per bar: predict, then update
against the close; kf = x[0], kf_slope = kf[i] − kf[i−1]. Long when the
close crosses above kf with kf_slope > 0; short when the close crosses
below kf with kf_slope < 0; exits on the bare opposite cross. The
velocity state is the point of the design — a plain price-only filter
lags badly in trends — but the same property makes the filter hug
price in chop and generate constant crosses.

Source: Kalman Filter trend strategy (DCAUT, TradingView) —
https://br.tradingview.com/script/u5C3sDUc-Kalman-Filter-DCAUT/

## Limitations

- Single 7-month crypto window — but 3,102 trades is a large sample
  for this window, so the negative result is the robust part.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- 1h timeframe only; the filter's chop behavior is timeframe-sensitive
  and was not tested elsewhere.
- The velocity state gives near-zero lag in steady trends but hugs
  price in chop — Kalman lags fast reversals by construction, and
  here the "lag" manifests as whipsaw, not slowness.
- R is a genuine sensitivity knob (sweep in CALIBRATION.md), but every
  tested value loses.
- No position pyramiding or regime filter: entries fire on every
  qualifying cross regardless of how many just failed.
