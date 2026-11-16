# Prior Day High/Low Breakout — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=48 bars.

## Results (shipped config: 0.1% filter, range filter 0.5x 20-day
median, 1.5xATR stop, 3xATR target, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 202 | 29.2% | -$3,348 | -33.5% | -2.80 | -37.7% | -$16.57 | 0.63 |
| ETH | 171 | 30.4% | -$1,789 | -17.9% | -1.46 | -24.1% | -$10.46 | 0.80 |
| HYPE | 231 | 29.4% | -$1,910 | -19.1% | -1.56 | -21.4% | -$8.27 | 0.82 |
| **Combined** | **604** | **29.6%** | **-$7,046** | — | — | — | **-$11.67** | — |

Breakouts fire constantly (long entries 104/79/134, short entries
109/102/116 for BTC/ETH/HYPE) and 604 of them become trades. Fees
total $5,146 against a -$7,046 net — fees are most of the damage on
HYPE ($1,385 of fees vs -$1,910 net) but the gross result is still
red on every coin. Win rates under 31% with a 2R target should be
near breakeven; the -$11.67/trade expectancy says the 2R target
almost never prints before the close-back-inside exit or the stop.

## Verdict: loser — the arbitrary session level whipsaws

Combined -$7,046 on 604 trades with expectancy -$11.67/trade and
profit factor 0.63–0.82 on every coin is a clear rejection. The
UTC-day boundary carries no real session information in a 24/7
market, so "breakouts" of it are mostly noise that closes back
inside the range within hours; the midnight-flat exit then books
small losses all day, every day. BTC is the worst leg (-$3,348,
Sharpe -2.80, MaxDD -37.7%).

## Calibration note

Shipped the specified 0.1% filter. A 0.05% – 0.1% – 0.2% filter
sweep is in CALIBRATION.md: every setting is deeply red combined
(-$7,629 / -$7,046 / -$7,780), and no setting is green on any coin.
The 0.1% filter was fixed a priori — adopted before the sweep, not
because of it.

## Mechanism

Each bar carries the prior UTC day's high/low and its 20-day median
range. A 1h close past the level by the 0.1% filter enters (skipped
if the prior-day range is < 0.5x its 20-day median). Exit on a close
back inside the range, the opposite level breaking, or the first bar
of a new UTC day (midnight flat, executed one bar into the new day
by the harness). 1.5xATR stop (≈ just inside the broken level),
3xATR target (2R), 24-bar max hold.

Source: PDH/PDL breakout —
https://www.quantsapp.com/backtesting/strategies/pdh-pdl-breakout-futures-and-option-buy

## Limitations

- Single 8-month crypto window; 604 trades is a decent sample and
  the loss is spread across all three coins.
- The UTC boundary is arbitrary for 24/7 crypto; the result is
  evidence against the level, not against session breakouts in
  markets with a real close.
- The 1.5xATR stop is an approximation of the textbook
  just-inside-the-level stop, not the literal level (see risk.py).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped filter on this window (see CALIBRATION.md).
