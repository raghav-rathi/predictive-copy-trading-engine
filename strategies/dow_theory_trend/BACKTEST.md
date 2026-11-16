# Dow Theory Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: 5-bar pivots, 33–66% pullback, volume
filter, 2xATR stop, 4xATR target, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 90 | 34.4% | -$917 | -9.2% | -1.06 | -12.8% | -$10.19 | 0.80 |
| ETH | 87 | 31.0% | -$1,562 | -15.6% | -1.71 | -15.6% | -$17.95 | 0.66 |
| HYPE | 85 | 40.0% | +$469 | +4.5% | +0.55 | -8.8% | +$5.52 | 1.12 |
| **Combined** | **262** | **35.1%** | **-$2,009** | — | — | — | **-$7.67** | — |

Signal gates fire on every coin (long entries 150/117/147, short
entries 80/82/109 for BTC/ETH/HYPE), but only 262 of those signals
become trades — the rest arrive while a position is already open or
fail the warmup. Fees total $2,131 against a -$2,009 net, so the
gross result is roughly breakeven before costs and the fee drag
turns it into a clear loser.

## Verdict: loser — late entries, fee drag, no edge

Combined -$2,009 on 262 trades with expectancy -$7.67/trade is not
noise, it is a losing system: BTC and ETH are both red with Sharpe
below -1, and the only green coin (HYPE, +$469, Sharpe +0.55) does
not survive a fee haircut on its own ($437 of fees for +$469 net).
The Dow structure confirms trends after they have already run, and
the 33–66% pullback + breakout entry buys the top of the pullback
more often than the start of a new leg.

## Calibration note

Shipped the specified 5-bar pivots. A 3 – 5 – 7 pivot sweep is in
CALIBRATION.md: every setting is red combined (-$482 / -$2,009 /
-$1,151), and no setting is green on more than one coin. The 5-bar
setting was fixed a priori — adopted before the sweep, not because
of it.

## Mechanism

Strict 5-bar pivots mark swing highs/lows (confirmed 2 bars late, no
lookahead). HH+HL = uptrend, LH+LL = downtrend. The pullback is
measured against the frozen leg that formed the last swing extreme,
so the pullback's own swing low cannot reset the range mid-pullback.
Enter on a close past the last swing extreme after a 33–66%
pullback, with breakout volume above its 20-bar mean. Exit on a
structure break (lower low / higher high) or a >66% retracement.
2xATR stop (≈ the last swing extreme), 4xATR target (2R), 120-bar
max hold.

Source: Dow Theory —
https://finabase.io/learn/technical-analysis/dow-theory

## Limitations

- Single 8-month crypto window; 262 trades is a thin sample, but the
  loss is spread across two of three coins, not one bad leg.
- The 2xATR stop is an approximation of the textbook swing-extreme
  stop, not the literal level (see risk.py).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped pivot size on this window (see CALIBRATION.md).
