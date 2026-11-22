# BTC Breakout Trend Climber — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: BTC/ETH 6,040 bars, HYPE 6,038 bars,
2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 3.5xATR(10) stop, 3x
leverage cap, $10k start, long/short. WARMUP=610 bars.

## Results (shipped config: prior-600-bar Donchian OR BB(50,
2.1σ, EMA mid) breakout; 3.5xATR(10) stop, 11.0xATR(10) trail;
opposite-breakout exit)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 52 | 23.1% | -$527 | +0.3% | +0.11 | -14.3% | -$10.13 | 0.86 |
| ETH | 50 | 22.0% | +$673 | +12.0% | +0.96 | -14.6% | +$13.47 | 1.18 |
| HYPE | 38 | 50.0% | +$2,175 | +22.9% | +1.84 | -6.7% | +$57.24 | 2.13 |
| **Combined** | **140** | **30.0%** | **+$2,322** | — | — | — | **+$16.59** | — |

Fees: BTC $328, ETH $281, HYPE $110 (total $719).
Net % is the equity-curve return; Net $ sums closed trades
only, so the two disagree on BTC (+0.3% vs -$527) because a
position was still open, marked to market, at the window end.

## Verdict: net positive, but carried by one coin — not proven

140 trades is a real sample, and the combined +$2,322 (+23% of
the $10k start across three coins, before the open-position
mark) is the best combined result of the batch's breakout-style
entries. But the composition is lopsided:

- HYPE contributes $2,175 of the $2,322 — 94% of the profit —
  on 38 trades at a 50% win rate and PF 2.13. That leg looks
  like a genuine trend-capture: the 11xATR trail lets HYPE's
  long 2026 uptrend runs develop.
- BTC and ETH are the classic breakout-chasing profile: ~22-23%
  win rates, PF 0.86-1.18, expectancy -$10 / +$13. Most
  breakouts fail into the 3.5xATR stop; the few that run pay for
  the churn on ETH and roughly break even on BTC.
- Max drawdown is -14% on both BTC and ETH — the wide trail
  lets losers run to the full stop distance repeatedly, and
  the strategy is fully exposed to the Nov 2026 selloff regime
  on the short side (mirrored entries) without any regime
  filter.

Stated plainly: the mechanism works where a clean trend exists
(HYPE) and churns where it doesn't (BTC/ETH range-breakout
noise). One 8-month window, one coin driving the result, no
out-of-sample check — this is a promising candidate for a
longer-window / more-coin validation, not a proven edge. Do not
quote the combined +$2,322 without the HYPE concentration.

## Mechanism

Prior-600-bar Donchian breakout OR BB(50, 2.1σ, EMA mid)
breakout; mirror for shorts; opposite breakout exits;
3.5xATR(10) stop, 11.0xATR(10) chandelier trail, no target, no
max hold. All params fixed a priori; no optimization. The
single-ATR-window deviation from the source's staged 5/15/10
ATR exit is documented in CALIBRATION.md.

Source: QuantConnect community backtest — BTC Breakout Trend
Climber
(https://www.quantconnect.com/terminal/cache/embedded_backtest_ad553ee3018fa48c5a0395a33ba8b2dd.html).

## Limitations

- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- HYPE concentration: the combined result does not survive
  removing the HYPE leg.
- The source's reported Sharpe 2.42 (long-only, BTC, its own
  window) does not reproduce here — different window, mirrored
  shorts, and the single-ATR mapping all change the result.
- Never tune the shipped parameters on this window.
