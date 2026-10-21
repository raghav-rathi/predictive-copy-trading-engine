# Holy Grail — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:00 UTC
(ms `[1773446400000, 1792590584428)`): 5,296 bars BTC/ETH, 5,294 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: ADX(14) > 30 and rising, EMA(20) touch,
buy-stop above/below the touch bar's high/low, exit on a close through
the average or ADX < 20, 2xATR stop, 3xATR trail, 100-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 3 | 0.0% | -$260 | -2.6% | -2.70 | -2.8% | -$86.75 | 0.00 |
| ETH | 5 | 20.0% | -$164 | -1.6% | -0.97 | -2.3% | -$32.84 | 0.46 |
| HYPE | 7 | 42.9% | +$287 | +2.9% | +0.94 | -2.4% | +$41.07 | 1.77 |
| **Combined** | **15** | **26.7%** | **-$137** | — | — | — | -$9.13 | — |

## Verdict: no evidence of edge — the setup barely trades on 1h crypto

Fifteen trades across three coins in seven months is not a sample, it
is a rounding error. Combined -$137 with expectancy -$9/trade, and the
per-coin reads point in different directions (HYPE green on 7 trades,
BTC 0-for-3). Nothing here can be called a winner or a loser with a
straight face.

The binding constraint is selectivity, not direction: ADX(14) > 30
**and rising** on 1h bars is a rare regime in this window, so the
"first pullback to the average in a strong trend" setup that Raschke
designed for daily charts almost never arms on the hourly. Lowering
the threshold to 25 (see CALIBRATION.md) roughly doubles the trade
count (34 combined) and the combined result gets *worse* (-$347) —
more trades, still no edge. Raising it to 35 leaves 6 trades total.
The setup is starved at any threshold in this regime.

## Calibration note

Shipped the specified ADX threshold of 30. A 25/30/35 threshold sweep
is in CALIBRATION.md: 25 trades more and loses more, 35 trades almost
nothing. 30 stays as the registry config — fixed a priori, and the
sweep offers no better alternative to adopt.

## Mechanism

Regime: close on the trend side of EMA(20) with ADX(14) above the
threshold and rising. Touch bar: low (high) tags the EMA(20) but the
close holds the trend side. Entry: next bar closes through the touch
bar's high (low) — a simulated buy/sell-stop. Exits: close back
through the average, or ADX falls under 20 (the trend faded). 2xATR
hard stop, 3xATR chandelier trail, 100-bar max hold. Every value on
bar i uses data through bar i's close only; execution is next-bar
open.

Source: Holy Grail (Linda Raschke & Larry Connors, Street Smarts) —
https://www.tradingsetupsreview.com/the-holy-grail-trading-setup/

## Limitations

- 15 combined trades: far too thin for any verdict; the "no edge"
  read is about absence of evidence, not evidence of absence.
- ADX > 30 + rising on 1h crypto is a rare regime — the daily-chart
  setup does not transfer cleanly to the hourly.
- Single 7-month window; funding unmodeled; next-bar-open execution
  vs the idealized stop entry.
- Do not trade this on the evidence here.
