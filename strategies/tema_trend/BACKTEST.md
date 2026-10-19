# TEMA Trend (Patrick Mulloy) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 00:00 UTC → 2026-10-19 13:00 UTC (5,247 bars BTC/ETH; 5,245 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 2.5xATR stop, 3x leverage cap,
$10k start. WARMUP=260 bars (SMA200 spin-up).

## Results (shipped config: TEMA(20) vs TEMA(50) cross with SMA200 regime
filter; long on cross-up above SMA200, short on cross-down below SMA200,
exit on cross back; 2.5xATR stop, 3xATR chandelier trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 119 | 27.7% | -$1,750 | -17.5% | -2.10 | -20.4% | -$14.71 | 0.66 |
| ETH | 124 | 32.3% | -$250 | -2.5% | -0.16 | -15.8% | -$2.02 | 0.95 |
| HYPE | 98 | 42.9% | +$2,131 | +21.3% | +2.14 | -6.1% | +$21.75 | 1.63 |
| **Combined** | **341** | **33.7%** | **+$131** | — | — | — | **+$0.39** | — |

## Verdict: flat overall (HYPE-only edge, not robust)

Combined +$131 on 341 trades is noise — expectancy +$0.39/trade against
~$9/trade in fees. The coin split is the whole story: HYPE prints a
genuinely good run (+$2,131, Sharpe 2.14, PF 1.63, maxDD only −6.1%)
while BTC loses −$1,750 (Sharpe −2.10) and ETH bleeds −$250. One coin
winning on one 7-month window is not a robust edge; it reads as
HYPE-specific trend regime (HYPE trended cleanly while BTC/ETH chopped),
not as TEMA alpha. The SMA200 regime filter does its job — entries only
with the long-term trend — but on 1h crypto the TEMA(20/50) cross still
lags the turns it needs to catch, and the 2.5xATR stop eats the whipsaws.

## Calibration note

Shipped exactly the specified parameters (TEMA 20/50, SMA200 filter,
2.5xATR stop, 3xATR trail, 120-bar max hold, WARMUP=260). A faster
TEMA(10,30) variant is reported in CALIBRATION.md — it loses on every
coin (combined −$4,162 on 635 trades) and wipes out the HYPE edge
entirely, confirming the faster cross is pure whipsaw. The specified
slower pair stays.

## Mechanism

TEMA(n) = 3·EMA1 − 3·EMA2 + EMA3 (EMA1 = EMA(close,n), EMA2 = EMA(EMA1,n),
EMA3 = EMA(EMA2,n)) — Patrick Mulloy's lag-reduced trend line. TEMA20
vs TEMA50 cross, gated by the SMA200 regime filter: long on cross-up
with close above SMA200, short on cross-down with close below SMA200;
exit when the TEMA cross flips against the position. 2.5xATR hard stop
(wider than usual — TEMA whipsaws on 1h crypto), 3xATR chandelier
trailing to let trends run, no fixed target (the cross-back manages the
trade), 120-bar max hold.

Sources:
- https://abovethegreenline.com/what-is-the-triple-exponential-moving-average-tema/
- https://www.definedgesecurities.com/library/tema/

## Limitations

- Single 7-month crypto window; no bull-market or multi-year sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- The HYPE-only win is a single-coin, single-window result — treat as
  hypothesis ("TEMA trend works on clean-trending alts"), not evidence.
- SMA200 needs 260 bars of warmup; the first WARMUP bars are warmup-only.
