# Jurik RSX — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=45 bars.

## Results (shipped config: Jurik RSX length 14, long on a cross above
50 with RSX rising, short mirrored, exit on a cross back through 50
or RSX hitting 80/20, skip flat RSX, 1.5xATR stop, 2xATR target,
72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 339 | 42.8% | -$1,787 | -17.6% | -0.97 | -32.1% | -$5.27 | 0.90 | $4,836 |
| ETH | 355 | 38.3% | -$3,825 | -38.0% | -2.77 | -44.4% | -$10.78 | 0.78 | $3,577 |
| HYPE | 336 | 41.1% | -$1,558 | -15.2% | -0.87 | -23.0% | -$4.64 | 0.90 | $1,992 |
| **Combined** | **1,030** | **40.7%** | **-$7,171** | — | — | — | **-$6.96** | — | **$10,405** |

Signal gates fire on every coin (long entries 170/178/169, short
entries 170/180/169 for BTC/ETH/HYPE). Profit factors of 0.78–0.90
and win rates of 38–43% say the same thing on all three coins: the
smoothed 50-line cross is late to every regime change, and the
2xATR target is reached less often than the 1.5xATR stop.

## Verdict: loser, but the least bad of the batch

Combined -$7,171 across 1,030 trades — the smallest dollar loss of
the four batch-37 strategies, and the only one with profit factors
near 0.90 on two coins. That is still a clear loss: expectancy
-$6.96/trade against ~$10.10/trade in fees, and no coin is green.
RSX's smoothness removes the whipsaw but not the lag — a 50-line
cross on a triple-smoothed oscillator confirms a move that has
already happened.

## Calibration note

Shipped the specified length 14. A 7 – 14 – 21 sweep is in
CALIBRATION.md: no setting is green on any coin; length 21 is least
bad combined (-$4,955) but still red everywhere. The length 14 was
fixed a priori — adopted before the sweep, not because of it.

## Mechanism

RSX (public reconstruction of Jurik's smoothing, per Wickra):
f18 = 3/(length+2), f20 = 1−f18; each stage is a double-EMA with
overshoot (a = f20·a + f18·in; b = f18·a + f20·b; out = 1.5a − 0.5b);
signed price change and absolute change each run through three
cascaded stages; RSX = clamp((v14/v1C + 1)·50, 0, 100), 50 when
v1C = 0. Long on a cross above 50 with RSX rising; short mirrored.
Exit on a cross back through 50 or RSX hitting 80/20. Skip entries
while RSX is flat (|ΔRSX| < 0.5 for 3 bars). 1.5xATR stop, 2xATR
target, 72-bar max hold.

Source: RSX (Jurik Research; Wickra docs) —
https://docs.wickra.org/Indicators/Indicator-Rsx

## Limitations

- **Reconstruction, not Jurik's exact code.** Jurik's internals
  are proprietary; this is the widely ported public RSX algorithm
  (see indicators.py). Values will differ from Jurik's own RSX.
- The smoothing that kills the whipsaw also adds lag — 50-line
  crosses confirm moves late, and the 1.5xATR stop fires first.
- Single 8-month crypto window; 1,030 trades at ~$10.10/trade in
  fees; funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped length on this window (see CALIBRATION.md).
