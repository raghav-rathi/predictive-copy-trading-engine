# Darvas Box — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,030 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 1.5xATR safety stop, 3x leverage cap, $10k start.

## Results (shipped config: box = 60-bar high unbroken for 3 bars, breakout volume > 1.25x SMA20, exit on close below box floor)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 37 | 27.0% | -$1,170 | -11.7% | -1.68 | -20.0% | -$31.61 | 0.53 |
| ETH | 29 | 34.5% | +$2,707 | +27.1% | +1.82 | -8.8% | +$93.35 | 2.35 |
| HYPE | 41 | 36.6% | +$443 | +4.4% | +0.49 | -9.5% | +$10.79 | 1.19 |
| **Combined** | **107** | **32.7%** | **+$1,980** | — | — | — | +$18.51 | — |

## Verdict: MIXED

Honest read: this is not a shipped-and-done winner. ETH is genuinely good
(Sharpe 1.82, profit factor 2.35, expectancy $93/trade), HYPE is borderline
(Sharpe 0.49, profit factor 1.19 — one bad trade away from zero), and BTC is
a clear loser (Sharpe -1.68, -20% max drawdown, profit factor 0.53). The
combined +$1,980 / +19.8% is real money on paper but it leans almost
entirely on the ETH sample. The mechanism is the original Darvas long-only
box breakout: it wants trending, range-breaking markets; BTC spent this
7-month window mostly chopping through boxes and the 1.5xATR safety stop plus
the box-floor exit bled on every fakeout. Fees ($1,085 combined) are
material but not the story on BTC — profit factor 0.53 means the gross edge
is absent there.

## Calibration note

Implementation deviation from the literal task spec, recorded here on
purpose: confirmation is evaluated on the PRIOR bar
(`box_confirmed.shift(1)`), not the signal bar. The breakout bar's own high
exceeds the box top by construction, so requiring
`h[i], h[i-1], h[i-2] < box_top[i]` on the signal bar yields exactly zero
trades — I verified this by construction before choosing the prior-bar form,
which preserves the stated intent (trade only confirmed boxes). Unit tests
pin both behaviors: the on-bar confirmation is False on the breakout bar,
and entries fire only when the prior bar's box was confirmed.

What survived contact with data: the volume filter. See CALIBRATION.md for
the 2-variant sweep (30-bar window; 1.0x volume multiplier).

## Mechanism

Box top = max high over the trailing 61-bar window excluding the last
3 bars; confirmed when the 3 most recent highs all fail to break it. Entry:
prior close at/below the prior box top, current close breaks above, prior
box confirmed, breakout volume > 1.25x SMA(20). Exit: close below the box
floor (min low since the bar where the top was set). Long-only. 1.5xATR
hard stop as safety net; no trailing, no target, no max hold.

Source: Darvas Box (Nicolas Darvas) — MQL5 Part 7 —
https://www.mql5.com/en/articles/24111

## Limitations

- Single 7-month crypto window; BTC's sample was chop-dominated.
- Funding unmodeled (longs would have paid it in this window).
- Next-bar-open execution vs idealized breakout entry — the volume-confirmed
  close is chased at the following open.
- 60-bar window / 1.25x volume are fixed; only the 2-variant sweep was run.
- Survivorship of the "combined" number: ETH carries it; treat as one
  good sample, not three independent validations.
