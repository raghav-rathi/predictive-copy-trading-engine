# Fractal Breakout (Bill Williams) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 00:00 UTC → 2026-10-19 13:00 UTC (5,247 bars BTC/ETH; 5,245 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=260 bars (200-bar SMA + fractal confirmation lag).

## Results (shipped config: 5-bar fractals, 2 bars each side, confirmed
2 bars late with levels forward-filled; long on close crossing above the
last confirmed up-fractal level with close > SMA200; short mirror; exits
on a cross back across the fractal level or an opposing fractal break;
2xATR stop, 80-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 316 | 29.4% | -$3,454 | -34.5% | -3.60 | -36.0% | -$10.93 | 0.61 |
| ETH | 305 | 26.2% | -$2,936 | -29.4% | -2.70 | -33.4% | -$9.63 | 0.66 |
| HYPE | 324 | 30.2% | -$1,562 | -15.6% | -1.68 | -18.6% | -$4.82 | 0.80 |
| **Combined** | **945** | **28.7%** | **-$7,952** | — | — | — | -$8.41 | — |

## Verdict: clear loser

Breakout-of-confirmed-fractal does not survive 1h crypto in this window:
~300+ trades per coin, sub-30% win rates, profit factors 0.61-0.80, and
Sharpe ratios of -1.68 to -3.60. The 2-bar confirmation lag means entries
fire after the fast part of the move on 1h bars, and the SMA200 gate does
not filter the whipsaw -- breakouts of 5-bar fractals in ranging crypto
are mostly false. Fees ($1,509-$3,028 per coin) hurt, but the gross edge
is negative regardless. Combined -$7,952 on 945 trades. Honest NO-GO.

## Calibration note

Fractal-size sweep (1/2/3 bars each side) in CALIBRATION.md: smaller
fractals trade more and lose more; larger fractals lose slightly less on
ETH/HYPE but stay negative everywhere. No size rescues the system.

## Mechanism

Up fractal at bar i: high[i] strictly greater than the highs of the 2
bars on each side; dn fractal: low[i] strictly lower than the lows of
the 2 bars on each side. Levels become visible 2 bars later (confirmation
lag) and are forward-filled, so the confirmed-level series is lookahead-
free by construction. Long when close crosses above the last confirmed
up-fractal level with close > SMA200 (documented substitute for the
Alligator trend gate); short is the mirror. Exits: cross back across the
fractal level, or an opposing fractal break (which also lets the position
flip). 2xATR hard stop (false breakouts are the dominant loss mode),
no trailing/target, 80-bar max hold.

Source: Aron Groups, Bill Williams Indicators (fractals) —
https://arongroups.co/technical-analyze/bill-williams-indicators/

## Limitations

- Single 7-month crypto window; no bull-market or multi-year sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry; the 2-bar
  confirmation lag plus 1-bar execution delay is a first-order effect
  for a breakout system.
- SMA200 substitutes for the Alligator (lips/teeth/jaw) -- a real
  Alligator gate might filter differently.
- 260-bar warmup discards the first ~11 days of data.
