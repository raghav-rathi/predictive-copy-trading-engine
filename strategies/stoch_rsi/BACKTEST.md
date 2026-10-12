# StochRSI — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-12
(~5,080 bars each).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: RSI(14), StochRSI(14), %K(3), %D(3), cross-in-zone entries, opposite-cross exits, 2xATR stop, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 450 | 28.7% | -$5,295 | -52.9% | -5.14 | -53.2% | -$11.77 | 0.56 |
| ETH | 430 | 33.3% | -$4,010 | -40.1% | -3.44 | -41.5% | -$9.33 | 0.69 |
| HYPE | 459 | 31.6% | -$4,855 | -48.5% | -5.12 | -51.1% | -$10.58 | 0.59 |
| **Combined** | **1,339** | **31.2%** | **-$14,159** | — | — | — | -$10.57 | — |

## Verdict: LOSER

Decisive and uniform: negative on all three coins with deeply negative
Sharpe (-3.4 to -5.1) and profit factors of 0.56–0.69. The system trades
430–459 times over 7 months — roughly twice a day — and the churn is the
kill shot: $3,531 in fees on BTC alone. The classic %K/%D cross whipsaws
relentlessly on 1h crypto; the zone gate (below 20 / above 80) does not
save it because StochRSI pins to 0/100 during trends and crosses
constantly on every counter-trend wobble. Win rate collapses to ~29–33%.

## Calibration note

Shipped the classic 14/14/3/3 without tuning first — the loss is not a
fitted artifact; it fails at the published parameters. The OS/OB sweep
(15/85, 20/80, 25/75, see CALIBRATION.md) shows no value in the stable
region — the system is structurally broken on 1h crypto, not mis-tuned.
What I verified: StochRSI is bounded 0–100, %K/%D smoothing matches the
definition, flat markets produce NaN (no fake signals), and indicators
are lookahead-free by truncation test.

## Mechanism

StochRSI = (RSI(14) - min RSI over 14) / (max RSI over 14 - min RSI over
14), %K = 3-bar SMA of StochRSI, %D = 3-bar SMA of %K. Long on %K crossing
above %D while both < 20; short on %K crossing below %D while both > 80;
exit on the opposite cross. 2xATR hard stop, no trailing/target, 168-bar
max hold.

Source: StochRSI (Tushar Chande & Stanley Kroll, 1994) — Investopedia —
https://www.investopedia.com/terms/s/stochrsi.asp

## Limitations

- Single 7-month window; the result is so uniformly negative that more data would not rescue it.
- Funding unmodeled (immaterial next to the gross loss).
- 1h timeframe only; the classic StochRSI is often applied on daily bars — that variant was not tested.
