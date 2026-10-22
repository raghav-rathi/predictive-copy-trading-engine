# Ulcer Index Regime Gate — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), sliced to the batch window 2026-03-14 00:00 UTC →
2026-10-21 23:59 UTC (ms `[1773446400000, 1792627199000)`; actual
data starts 2026-03-14 22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC
for HYPE): 5,301 bars BTC/ETH, 5,299 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long-only. WARMUP=60 bars.

## Results (shipped config: UI(14), calm < 5.0 gate on the prior-bar
ulcer, entry on a cross above the prior 20-bar Donchian high, exit
on a cross below the prior 10-bar Donchian low OR ulcer > 10.0,
1.5xATR stop, 2xATR chandelier trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 110 | 31.8% | -$649 | -6.5% | -0.38 | -16.4% | -$5.90 | 0.89 |
| ETH | 102 | 35.3% | +$1,051 | +10.5% | +0.82 | -15.8% | +$10.30 | 1.19 |
| HYPE | 123 | 34.1% | +$1,196 | +12.0% | +0.90 | -15.9% | +$9.72 | 1.16 |
| **Combined** | **335** | **34.0%** | **+$1,598** | — | — | — | +$4.77 | — |

Fees: BTC $1,670, ETH $1,257, HYPE $985.

## Verdict: combined green, but it is fee-bound noise, not a regime edge

Combined +$1,598 across 335 trades sounds fine until you look at
the legs:

- **BTC is a loser** (-$649, PF 0.89, Sharpe -0.38, expectancy
  -$5.90/trade). The Donchian breakout entry on BTC's 1h catches
  breakdowns in reverse as often as breakouts.
- **ETH and HYPE are marginal, not green.** ETH nets +$1,051
  against $1,257 in fees; HYPE nets +$1,196 against $985 in fees.
  Expectancies (+$10.30, +$9.72) are a couple of trades' worth of
  noise from zero, and the win rates sit at 34–35%.
- **The Ulcer Index gate did almost nothing.** Martin's 5/10
  thresholds were calibrated on daily equity closes; on 1h crypto
  bars UI(14) lives in a 0–4 band (BTC max 4.38 with zero bars
  above 5; ETH 0.51% of bars above 5; HYPE 3.49%; no bar on any coin
  ever above 10). The calm gate therefore passes ~always and the
  panic exit never fires — the strategy as shipped is effectively
  a plain 20-bar Donchian breakout / 10-bar Donchian-low exit
  long-only system, which is exactly what the calibration sweep
  shows (n=7 and n=14 produce literally identical trade sets).
  The "regime gate" is a costume.

The honest read: a Donchian-breakout long-only that nets +$1,598
with fees roughly equal to the profit. Not a loser, not an edge —
and the Ulcer Index component needs rescaling to the 1h timescale
before it can claim to be doing any work (see CALIBRATION.md).

## Calibration note

Shipped n=14 fixed a priori (the canonical Martin length) — no
in-sample selection. The n=7/14/28 sweep is in CALIBRATION.md:
combined +$1,598 / +$1,598 / +$1,345. The near-total insensitivity
is the UI thresholds being out of scale for 1h bars, not evidence
that n=14 is optimal.

## Mechanism

Ulcer Index (Peter Martin, 1987): pctdd = 100 × (close −
max(close, 14)) / max(close, 14); UI = √(mean(pctdd²)) over 14.
Long when the prior-bar ulcer < 5.0 (calm regime) and close
crosses above the prior 20-bar Donchian high; exit on a cross
below the prior 10-bar Donchian low or ulcer > 10.0. No shorts.
1.5xATR stop, 2xATR chandelier trail, 120-bar max hold.

Sources: https://en.wikipedia.org/wiki/Ulcer_index —
https://www.tradingview.com/support/solutions/43000564954

## Limitations

- Single 7-month crypto window; 335 trades is a thin sample and
  the combined green is fee-adjacent.
- BTC leg negative; ETH/HYPE legs marginal with fees ≈ net.
- The UI thresholds (5/10) are out of scale for 1h crypto bars —
  the regime gate is inert at these settings; recalibration must
  happen on walk-forward data, not this window (see
  CALIBRATION.md).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped length on this window.
