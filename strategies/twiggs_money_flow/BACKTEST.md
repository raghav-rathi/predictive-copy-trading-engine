# Twiggs Money Flow — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 00:00 UTC → 2026-10-19 13:00 UTC (5,247 bars BTC/ETH; 5,245 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars (Wilder EMA-21 spin-up).

## Results (shipped config: TMF = WilderEMA(mf,21)/WilderEMA(v,21),
mf = v*(2c-h-l)/true-range; long on cross above 0, short on cross below 0,
exit on cross back through 0; 2xATR stop, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 528 | 23.1% | -$5,570 | -54.6% | -3.64 | -61.0% | -$10.55 | 0.63 |
| ETH | 453 | 28.9% | -$3,100 | -30.7% | -1.70 | -42.0% | -$6.84 | 0.77 |
| HYPE | 420 | 29.3% | +$192 | +2.5% | +0.29 | -21.1% | +$0.46 | 1.01 |
| **Combined** | **1,401** | **26.8%** | **-$8,478** | — | — | — | **-$6.05** | — |

## Verdict: loser

The zero-line cross is a whipsaw machine on 1h crypto. 1,401 trades in
7 months (~6.6/day across the book) with a 26.8% win rate and profit
factor 0.63–0.77 on the majors — the entries chop in and out of every
range while the 2xATR stop bleeds on each false cross. Combined fees
($8,877) exceed the gross edge by an order of magnitude, but fees are
not the story: expectancy is negative before costs too. HYPE's +$192
(PF 1.01) is statistical noise, not a redeeming split. Sharpe −3.64 on
BTC with a −61% max drawdown is a system to avoid, not tune.

## Calibration note

Shipped exactly the specified parameters (Wilder 21, zero-line
crosses, 2xATR stop, 60-bar max hold, WARMUP=80). A faster TMF(14)
variant is reported in CALIBRATION.md — it loses *more* everywhere
(combined −$12,280 on 1,752 trades), confirming the problem is the
signal logic, not the smoothing length. No parameter rescue attempted;
the mechanism is rejected on this data.

## Mechanism

trange_i = max(h_i−l_i, |h_i−c_{i−1}|, |l_i−c_{i−1}|) — the true range,
so gap days don't distort the denominator the way Chaikin's fixed
(h−l) does. mf_i = v_i·(2·c_i−h_i−l_i)/trange_i (0 when trange_i = 0).
TMF = WilderEMA(mf,21) / WilderEMA(v,21), Wilder form = ewm(alpha=1/21)
as in strategies.base.atr. TMF > 0 = net inflow, TMF < 0 = net outflow.
Long on cross above 0, short on cross below 0; exit when TMF crosses
back through 0 against the position. 2xATR hard stop, no trailing /
target (the zero-line cross-back manages the trade), 60-bar max hold.

Source: Twiggs Money Flow — https://www.mql5.com/en/market/product/451

## Limitations

- Single 7-month crypto window; no bull-market or multi-year sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- 1,401 trades makes this a high-turnover system; fee/slippage
  assumptions dominate more than for slower systems.
- Wilder EMA-21 needs ~80 bars of spin-up; the first WARMUP bars are
  warmup-only.
