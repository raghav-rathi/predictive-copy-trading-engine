# Renko Brick Reversal — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00
UTC (ms `[1773525600000, 1792328400000)`; HYPE data starts
2026-03-15 00:00 UTC): 5,223 bars BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=220 bars.

**Brick sizes (mean ATR(14), first 200 bars):** BTC $507.48,
ETH $20.87, HYPE $0.60. Bricks printed: BTC 526, ETH 492, HYPE 1,219.

## Results (shipped config: brick = 1.0x ATR(14), long on a bullish
2-brick reversal after ≥ 3 down bricks, short on a bearish 2-brick
reversal after ≥ 3 up bricks, exit on the opposite 2-brick reversal,
2xATR stop, 3xATR trail, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 60 | 20.0% | -$2,139 | -21.4% | -3.00 | -24.8% | -$35.65 | 0.42 |
| ETH | 54 | 27.8% | -$1,449 | -14.5% | -1.99 | -19.1% | -$26.84 | 0.54 |
| HYPE | 131 | 30.5% | -$982 | -9.8% | -0.81 | -20.8% | -$7.50 | 0.85 |
| **Combined** | **245** | **27.3%** | **-$4,571** | — | — | — | **-$18.66** | — |

Entry signals fired on every coin (long/short): BTC 34/28,
ETH 27/29, HYPE 67/67.

## Verdict: a loser on all three coins

Combined -$4,571 across 245 trades, 27.3% win rate, expectancy
-$18.66 a trade, and no coin anywhere near breakeven. The 2-brick
reversal entry is the problem in its classic form on 1h crypto:
by the time 2 bricks have printed in the new direction, the move
is already 2+ ATRs extended, and the 2xATR stop sits right behind
the entry — the exit ledger proves it:

- **BTC: 59 of 60 exits were stops**, 1 by signal. ETH: 54 of 54
  were stops. The reversal exit almost never gets a chance — the
  stop fires first.
- **HYPE is the least bad** (-$982, PF 0.85, 39 of 131 exits by
  signal) because it prints far more bricks (1,219 vs ~500) and
  its runs extend further, so some reversals complete before the
  stop is hit. Still a loser.
- Fees ($1,387) are 30% of the net loss — the loss is the entries,
  not the costs.

## Mechanism

Renko bricks from 1h closes, brick size = mean ATR(14) over the
first 200 bars, fixed per coin. Long on a bullish 2-brick reversal
after ≥ 3 down bricks; short on a bearish 2-brick reversal after
≥ 3 up bricks. Exit on the opposite 2-brick reversal. 2xATR hard
stop, 3xATR chandelier trail, 200-bar max hold.

Source: Renko chart —
https://www.cmcmarkets.com/en-gb/technical-analysis/renko-charts

## Limitations

- Close-based Renko approximation, not tick Renko; intrabar
  reversals are invisible.
- Single 7-month crypto window; 245 trades is a thin sample, and
  the signal is structurally late — the entry chases a move that
  has already printed 2 bricks.
- The fixed brick size is set from the first 200 bars and never
  adapts to later volatility regimes.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped brick size on this window (see
  CALIBRATION.md — the 0.5x setting looks better in-sample and was
  deliberately not adopted).
