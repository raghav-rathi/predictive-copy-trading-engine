# Funding Squeeze Reversal — Backtest

**Data:** Hyperliquid `candleSnapshot` 1h bars + real hourly `fundingHistory`
(merged asof, backward — each bar sees only funding prints at/before its
open), BTC + ETH + HYPE, 2026-03-14 → 2026-10-10 (~5,080 bars each).
**Costs:** 0.045% taker fee + 0.01% slippage per side; funding PnL accrued
hourly from real fundingHistory (the fade-collects-funding leg is part of
the thesis — shorts earn positive funding).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. Warmup 96 bars.

## Results (shipped config: author thresholds — short fund8 > +0.030%,
long fund8 < −0.020%, vol > 1.5x SMA20, confidence ≥ 0.45, 3x-volume
violent guard, reversing exits, 2xATR stop, 3xATR chandelier, 12-bar cap)

| Coin | Signals | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 0 | 0 | — | $0 | 0.0% | — | — | — | — |
| ETH | 1 | 1 | 100% | +$52 | +0.5% | 0.53 | -0.8% | +$51.64 | inf (1 trade) |
| HYPE | 40 | 16 | 68.8% | +$385 | +3.8% | 1.29 | -3.3% | +$24.05 | 2.08 |
| **Combined** | **41** | **17** | **70.6%** | **+$436** | — | — | — | +$25.67 | — |

Fees paid: $49 combined. Funding earned: +$8.73 (the short book collects
positive funding, as the thesis expects).

## Verdict: MIXED — winner on HYPE, no-signal on BTC/ETH

On HYPE the strategy is a genuine winner: 16 trades, 68.8% win rate,
profit factor 2.08, Sharpe 1.29, max drawdown −3.3%. The mechanism works
exactly where funding extremes exist — HYPE's funding is the wildest of
the three (8h-sum max 0.064% vs 0.027% BTC / 0.024% ETH), closest to the
BNB dynamics the author calibrated on.

On BTC and ETH the author's literal thresholds (+0.030%/−0.020% per 8h)
are unreachable on Hyperliquid's tamer funding regime: BTC's 8h funding
sum never exceeded +0.027% in 7 months (99th pct: +0.0156%), so the short
leg fired zero times and the book sat flat. This is a threshold-scale
port gap, not a mechanism failure — the CALIBRATION.md sweep shows
loosening the thresholds destroys the edge rather than fixing it.

## Calibration note

Shipped the author's literal thresholds (see CALIBRATION.md): the
threshold-scale sweep {1.0x, 0.5x, 0.25x} confirms 1.0x is the only
scale with a positive combined book; 0.25x turns the system into
375-trade churn (−$1,334). The edge lives in genuine funding extremes,
and on this venue only HYPE produces them. What I verified: fund8 and
the confidence formula match hand computation (unit tests), funding
merge is lookahead-free by truncation test. What needs watching: 17
trades total is thin — the HYPE Sharpe is fragile, and a funding-regime
change (calmer HYPE funding) would silence the strategy the way BTC/ETH
already are.

## Mechanism

8h cumulative hourly funding > +0.030% with volume > 1.5x its 20-bar SMA
and weighted confidence ≥ 0.45 → SHORT (fade crowded longs); < −0.020%
→ LONG (fade crowded shorts). Skip when volume > 3x SMA (violent-spike
guard). Reversing exits + 2xATR hard stop + 3xATR chandelier trailing +
12-bar max hold.

DEVIATION (documented in indicators.py): the author's OI-divergence term
is dropped — Hyperliquid's public API exposes no historical OI series.
The 3x-volume guard is the author's own "violent OI move" guard
translated to volume.

Source: Funding Squeeze Reversal — beatp-bit (CoinMarketCap BNB HACK 2026) —
https://github.com/beatp-bit/funding-squeeze-reversal

## Limitations

- Single 7-month window; only 17 trades — Sharpe/PF estimates are noisy.
- Thresholds calibrated on BNB funding; BTC/ETH on HL never reach them.
- Next-bar-open execution; the 12-bar cap means funding accrual is small
  relative to price PnL, but it is modeled from real fundingHistory.
- Volume is the only crowding proxy left after dropping OI; a true
  OI-divergence filter would need an OI feed HL doesn't publish.
