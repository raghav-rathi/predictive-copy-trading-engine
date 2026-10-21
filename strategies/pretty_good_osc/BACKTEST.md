# Pretty Good Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:50 UTC
(ms `[1773446400000, 1792590633848)`): 5,296 bars BTC/ETH, 5,294 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: PGO = (c−SMA14)/SMA(ATR14,14), trigger 3.0;
long on cross above +3, short on cross below −3, exits on the cross
back through 0, 2xATR stop, 3xATR trail, 100-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 75 | 34.7% | -$456 | -4.6% | -0.46 | -12.1% | -$6.08 | 0.87 |
| ETH | 78 | 33.3% | -$797 | -8.0% | -0.79 | -11.9% | -$10.22 | 0.80 |
| HYPE | 48 | 39.6% | +$1,535 | +15.4% | +1.72 | -4.6% | +$31.98 | 1.69 |
| **Combined** | **201** | **35.8%** | **+$282** | — | — | — | +$1.40 | — |

## Verdict: a HYPE pocket inside an otherwise dead strategy

The combined +$282 is statistical noise — the honest read is that this
strategy does not work on the majors and has one bright, thinly
sampled leg on HYPE:

- **HYPE is the whole story** (+$1,535, Sharpe +1.72, PF 1.69,
  MaxDD -4.6%, expectancy +$32/trade): 48 breakout-thrust trades where
  the +3 ATR entry caught genuine continuation and the zero-cross exit
  banked it. Clean profile — but 48 trades is a thin sample for any
  "HYPE edge" claim.
- **BTC is noise** (-$456, PF 0.87, expectancy -$6/trade): the ±3 ATR
  trigger fires into thrusts that immediately mean-revert, and the
  zero-cross exit then exits at the mean — a round trip minus fees.
- **ETH is a weak loser** (-$797, PF 0.80, expectancy -$10.22/trade,
  Sharpe -0.79): ETH's 1h chop produces thrusts that fail more often
  than they continue, and the 2xATR stop eats the difference.
- 35.8% combined win rate with exits at the mean means the system
  structurally needs big, rare winners; on 7 months of data it only
  found them on HYPE.

## Calibration note

Shipped the specified trigger=3.0. A 2.0/3.0/4.0 trigger sweep is in
CALIBRATION.md: 4.0 is best combined in-sample (+$681) and best on
HYPE (+$1,412, PF 3.70, 18 trades), 2.0 is worst (-$2,954). The 3.0
trigger was fixed a priori — no in-sample adoption: it stays the
registry config despite 4.0 looking better on this window. The sweep
confirms the mechanism intuition: a wider trigger filters out the
BTC/ETH chop (BTC at 4.0 is nearly flat at -$93) at the cost of very
thin samples.

## Mechanism

Mark Johnson's Pretty Good Oscillator: PGO = (close − SMA(14)) /
SMA(ATR(14),14) — how far the close sits from its 14-bar mean, in
average true ranges (dimensionless). Entry is a breakout trigger: long
when PGO crosses above +3.0, short when it crosses below −3.0.
Exits take the trade off when the displacement decays: long exits on
PGO crossing back below 0 (close returned to its mean), short exits
on the cross above 0. No trailing, no fixed target — the
mean-reversion exit is the trade management. 2xATR hard stop, 3xATR
chandelier trail, 100-bar max hold.

Source: Pretty Good Oscillator (Mark Johnson) —
https://lightningchart.com/blog/trader/pretty-good-oscillator/

## Limitations

- The HYPE leg is 48 trades — promising but thin; the strategy's
  combined edge is +$282, i.e. nothing, without HYPE.
- BTC/ETH legs are negative with PF < 1; the ±3 ATR breakout trigger
  on 1h majors mostly captures moves that revert by the zero cross.
- The 4.0-trigger alternative is better in-sample but on 18–38
  trades per coin — do not adopt it on this evidence (see
  CALIBRATION.md).
- Funding unmodeled; next-bar-open execution vs idealized entry.
