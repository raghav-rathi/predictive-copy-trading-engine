# Fade-side backtest — notes and verdict

## Question
Mirror backtests show ~zero robust edge for copying winners. But the score
gate reliably identifies losers (rejected shadows lost money in every run).
Does **fading** wallets scoring ≤30 (taking the opposite side) show edge?

## Method
`backtest_fade.py` (stdlib + urllib, reuses `hyperliquid/scorer.py` +
`sizing.py`), 30d window (2026-09-02 → 2026-10-02), same 4 vaults as the
mirror tests, plus 4 known-bad vaults as a second universe:

- Fade entries at the target's fill price, side flipped (their long →
  our short), fragmented fills aggregated to one intent per
  (coin, direction) within 60s.
- Size = min($200, Kelly f* × 0.5 × $200) where f* is computed on the
  **inverted** closes (their −$X = our +$X). Skip when f* ≤ 0
  (no counter-edge). Pure losers (no winning closes) fade at full $200;
  pure winners are skipped — verified by unit test.
- Exits: proportional closes on target closes (their loss = our win) +
  SL 8% / TP 20% / trailing 2% / 24h max-hold on OUR inverse position,
  15m candles, same-candle SL+TP ties resolve to the stop.
- Costs: 0.035% taker + 0.02% slippage per side.
- Two modes on the 4 good vaults (fade-only; combined mirror≥65 + fade≤30),
  one mode on the 4 bad vaults (fade-only).

Inverse-PnL math hand-verified on a synthetic: target long 1.0 BTC @
$80,000, we short $200 (0.0025 BTC); target closes half @ $78,000 →
our leg gross +$2.50 / net +$2.3914; target closes rest @ $81,000 →
our leg gross −$1.25 / net −$1.3607. Exact to the cent.

## Results

| Mode | Universe | Trades | Net PnL | ex-top3 | Win rate | Fees |
|---|---|---|---|---|---|---|
| fade | 4 good vaults | 0 | $0.00 | — | — | $0.00 |
| combined | 4 good vaults | 3,715 | **+$214.45** | +$147.76 | 56.0% | $47.15 |
| fade_losers | 4 bad vaults | 0 | $0.00 | — | — | $0.00 |

**The fade trigger (score ≤30) never fired — not once in 248 vault-days
(8 vaults × 31 days).** Fade edge is UNTESTED, not refuted.

The 4 "known-bad" vaults (leaderboard 3M returns −26% to −90%) score
76–88 on trailing-30d TRUE realized PnL — e.g. songer1993.hl: +$25,597
realized, 62% WR, score 83.2. They genuinely recovered; the leaderboard
data was stale. They are not fade candidates on recent form.

## Two engine bugs found (both fixed in `hyperliquid/scorer.py`)

1. **`closedPnl` is a numeric STRING, and the scorer ignored it.**
   `_fill_pnl` did a strict `isinstance(pnl, (int, float))` check, so
   every live fill fell back to FIFO reconstruction. Measured impact:
   songer1993.hl 30d realized was understated 45% by FIFO
   (+$14,021 vs true +$25,597); winning-fortunes was off 2.5%.
   **Every scorer output before this fix (all mirror backtests, the
   live paper tracker) ran on FIFO approximations, not true PnL.**
   Fixed: coerce numeric strings to float.

2. **(Consequence of #1)** With TRUE realized PnL, the mirror book
   (Kelly 0.5 + trailing, i.e. Variant C config) reprices from
   +$34.55 / 1,335 trades / 51.3% WR to **+$214.45 / 3,715 trades /
   56.0% WR, ex-top3 +$147.76** — broad-based, not outlier-driven.
   The truer Kelly edge estimate takes ~3× more trades at better sizes.
   This is a data correction, not a strategy change — but it materially
   improves the mirror verdict to +2.14% / 30d.

## Why the fade gate never fires (structural)

- ~25 of 100 score points are free for any active wallet
  (sample_size 15 + recency 10), so ≤30 demands catastrophic realized
  stats: roughly <20% win rate AND terrible profit factor AND high
  drawdown, sustained 30 days.
- The 10-close minimum means quiet wallets are "unscored", never faded.
- Net effect: on real vault universes the fade path is near-dead code.

## Verdict

- **Fading losers: UNTESTED.** No fade signal occurred in either
  universe. The hypothesis is not disproven — there was simply nothing
  to fade.
- **Mirror verdict upgraded by the data fix:** +$214.45 (+2.14%/30d),
  56% WR, ex-top3 +$147.76. Still a 30d/4-vault sample — not a live
  guarantee — but no longer "zero edge".
- **Recommended engine changes before live capital:**
  (a) keep the closedPnl fix (done); (b) re-examine the fade threshold —
  ≤30 may be unreachable by construction; consider fading the 30–50
  "watch" band or scoring unrealized PnL so equity-bleeders with green
  realized closes can't score "copy"; (c) re-run the mirror baseline +
  tuning grid on TRUE PnL, since all prior tuning was FIFO-based.

## Files
- `backtest_fade.py` — parameterized (fade / combined / fade_losers)
- `backtest_fade_summary.json`, `backtest_fade_combined_summary.json`,
  `backtest_fade_losers_summary.json`
- `backtest_fade_trades.csv`, `backtest_fade_combined_trades.csv`,
  `backtest_fade_losers_trades.csv` (large; local only)
- `backtest_fade.log`
