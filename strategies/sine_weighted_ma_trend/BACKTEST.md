# Sine-Weighted MA Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC
(ms `[1773525600000, 1792328400000)`): 5,223 bars BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: SWMA(20) vs SWMA(40) crossover, exits on the
opposite cross, 2xATR stop, 3xATR trail, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 159 | 30.8% | -$1,919 | -19.5% | -1.51 | -30.0% | -$12.07 | 0.74 |
| ETH | 169 | 40.2% | +$1,132 | +11.3% | +0.84 | -19.3% | +$6.70 | 1.15 |
| HYPE | 160 | 36.2% | +$1,487 | +15.2% | +1.11 | -9.1% | +$9.29 | 1.19 |
| **Combined** | **488** | **35.9%** | **+$700** | — | — | — | +$1.43 | — |

Signal gates fire on every coin (long entries 80/84/80, short entries
80/85/81 for BTC/ETH/HYPE). Exit reasons are stop-dominated: 132–142
stops vs 27 signal exits per coin — the laggy cross enters late and
the 2xATR stop usually fires before the opposite cross can.

## Verdict: break-even noise, not a strategy

Combined +$700 across 488 trades is a rounding error: expectancy
+$1.43/trade against ~$8.20/trade in fees, and the sign flips if any
single HYPE leg goes differently. BTC is a genuine loser (-$1,919,
Sharpe -1.51, MaxDD -30.0% — the deepest hole of the three), ETH and
HYPE are modestly green but with MaxDDs of -19.3% and -9.1% for
+$1,132 / +$1,487 respectively. The SWMA's center-weighted lag means
entries chase legs that are already half over; the 2xATR stop then
absorbs the reversal. Nothing here survives a fee or slippage haircut.

## Calibration note

Shipped the specified 20/40. A 10/20 – 20/40 – 30/60 sweep is in
CALIBRATION.md: no setting is green on all three coins, and the
combined winner (20/40, +$700) beats 10/20 (-$1,159) and 30/60
(-$2,391) only by being the least bad. The 20/40 setting was fixed
a priori — adopted before the sweep, not because of it.

## Mechanism

SWMA: weights sin(π·(i+1)/(n+1)) over the last n closes, normalized
by their sum. Long when SWMA(20) crosses above SWMA(40), short on a
cross below; exits on the opposite cross. 2xATR hard stop, 3xATR
chandelier trail, 200-bar max hold.

Source: Sine-Weighted Moving Average (Patrick Lafferty, 1999) —
https://www.luxalgo.com/library/concept/sine-weighted-ma/

## Limitations

- Single 7-month crypto window; 488 trades is a thin sample and the
  combined result is statistically indistinguishable from zero.
- BTC leg is negative with a -30% drawdown; ETH leg's fees ($1,413)
  exceed its net (+$1,132).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped lengths on this window (see CALIBRATION.md).
