# Backtest notes — six-bot desk, run 2026-10-04

## Auditor verdict: NO-GO

| # | Go / no-go rule (locked before the run) | Actual | Verdict |
|---|------------------------------------------|--------|---------|
| 1 | trades ≥ 40 | 46 | PASS |
| 2 | win rate ≥ 33% | 2.17% (1/46) | FAIL |
| 3 | expectancy ≥ +0.40R | −0.96R | FAIL |
| 4 | max drawdown ≤ 20% | 37.94% | FAIL |

- Net PnL: **−$3,794.18** on $10,000 paper equity (−37.9%). Total: **−44.25R**.
- Exit reasons: 45× STOP, 1× STALE (the lone winner, +0.22R). No ANCHOR exits.
- 582 bear flips → 46 trades. 790 skipped alerts journaled, dominated by
  SUPERSEDED (421: newer flip alerts replacing pending ones), TESTED_ZONE
  (254), NO_FRESH_ZONE (83), EXPIRED (16), ZONE_INVALIDATED (12),
  POSITION_ALREADY_OPEN (4).
- 378 bullish flips logged as context only, never traded (short-only desk).

## "What SKIPPED would have done" (auditor split)

| Ledger | n | Win rate | Expectancy | Net |
|--------|---|----------|------------|-----|
| Clean alerts (no skip flag) | 28 | 3.57% | −1.09R | −$2,494.89 |
| Flagged SKIP (mostly TESTED_ZONE), auto-taken | 18 | 0.00% | −0.76R | −$1,299.29 |
| PRIME-tagged | 18 | 5.56% | −1.05R | — |
| Non-PRIME | 28 | 0.00% | −0.91R | — |

Skipping tested zones would not have saved the desk; both ledgers lose.

## Per-coin

| Coin | Trades | Win rate | Net |
|------|--------|----------|-----|
| BTC | 6 | 0% | −$707 |
| ETH | 0 | — | $0 |
| SOL | 3 | 33% | −$219 |
| HYPE | 5 | 0% | −$324 |
| DOGE | 2 | 0% | −$203 |
| XRP | 7 | 0% | −$404 |
| BNB | 2 | 0% | −$196 |
| ADA | 6 | 0% | −$523 |
| AVAX | 3 | 0% | −$179 |
| LINK | 4 | 0% | −$515 |
| NEAR | 3 | 0% | −$236 |
| ARB | 5 | 0% | −$288 |

No coin was profitable. ETH produced flips but no fillable setups.

## Method

- Data: Hyperliquid `candleSnapshot` (public), 1d + 4h + 1h. Window
  2026-03-10 → 2026-10-04 (~209 days): the API retains 1H candles only back
  to 2026-03-10 (verified against 15m/30m/2h; 1d/4h go back 12+ months and
  are used for indicator lookback).
- Costs: 0.05% taker fee/side, 0.02% slippage/side (price worsened).
- Entries at the next 1H open after 1H confirmation; stop = zone top, no
  buffer; gap-throughs filled at the open. One position per coin.
- R = net PnL ÷ total risked (initial 1% + 0.5% per add, max 2 adds).
- Max drawdown on a daily mark-to-market equity curve.
- Thresholds were locked in `DESK_RULES.md` before the run; nothing was
  re-tuned after seeing results. Reproduce with:
  `python3 sixbot/data.py && python3 sixbot/backtest.py --out sixbot/results`

## Reading the result

The failure mode is uniform, not a data quirk: 45 of 46 trades stopped out
at the zone top. Shorting 1H rejections of the highest fresh FVG with a
bufferless stop meant the stop sat just above a wick the market had just
printed — wicks get retested. Thin zones additionally created leverage
pathologies (e.g. a 0.07% stop distance → ~13× notional → round-trip fees
alone exceeded 1R). The desk, implemented exactly per its charters, does
not survive contact with 2026 price action in this window.
