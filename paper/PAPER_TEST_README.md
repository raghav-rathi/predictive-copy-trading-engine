# Paper Trading Test — Hyperliquid Copy Engine on Live Mainnet

`paper_tracker.py` runs the copy engine's decision logic against **live
Hyperliquid mainnet fills** on a 30-minute cron cadence, to answer one
question over 3–4 days: *does copying scored vaults/wallets make money
after fees?*

## How it works

Each run, per target (vault or wallet address in `paper_targets.json`):

1. **Score** (at most every 6h, trailing 30d of fills): the exact engine
   logic — `scorer.score_wallet` / `classify` from
   `~/workspace/copytrade-robinhood/hyperliquid/` — FIFO realized PnL,
   time-weighted win rate / profit factor, consistency across windows,
   drawdown, minimum-sample guard. **Copy only if score ≥ 65 AND ≥ 10
   closed trades.** (Note: the scorer expects second-epoch timestamps;
   live fills are ms — the tracker normalizes; without this
   `score_wallet` overflows.)
2. **Fetch** fills since the per-target watermark (`userFillsByTime`,
   chunked time windows), **dedup by fill hash** (a fill is never
   processed twice, even across restarts/crashes), skip `Settlement`
   fills.
3. **Opens**: fragment-clustered into one intent per (coin, direction)
   within 120s, then the copy gate: classification must be `copy`;
   size = **2% of the $10,000 paper account** ($200 max), shrunk by the
   fractional-Kelly cap from the target's measured edge
   (`sizing.kelly_fstar` — skipped entirely when edge ≤ 0); one paper
   position per (target, coin).
4. **Closes**: the matching paper position is closed **proportionally**
   (`closePct = fill.sz / |target startPosition|`) at the target's fill
   price.
5. **Independent exits** against live `allMids`: stop-loss 8%,
   take-profit 20%, trailing 2%, max hold 24h (trailing peak persisted
   in state so it survives restarts).
6. State saved **atomically** (tmp + rename); one bad target never
   kills the run; missing/corrupt state starts fresh with a warning.

## Files

| File | Role |
|---|---|
| `paper_tracker.py` | the tracker (stdlib only) |
| `paper_targets.json` | targets; `0xREPLACE_ME_*` placeholders are skipped |
| `paper_trades.csv` | every paper fill (append-only; `#` preamble states assumptions) |
| `paper_summary.json` | rebuilt from the CSV every run (self-healing) |
| `paper_state.json` | watermarks, seen fill hashes, open positions, cached scores |
| `paper_tracker.log` | run log |

## Cost assumptions (in CSV preamble + `paper_summary.json.assumptions`)

- Taker fee **0.035%** + slippage **0.02%** per side → **0.055%/side**,
  0.11% round-trip, charged on every paper fill.
- `realized_pnl_usd` on closes is **net of both sides' fees**.
- Paper fills assume a **full fill at the target's fill price**; no
  market impact; no funding payments modeled; exits evaluated on the
  30-min cadence against public mids.

## Reading the CSV

Columns: `ts, target, coin, side, action, size, price, fee_usd,
realized_pnl_usd, paper_equity_usd, reason, fill_hash`.
`action` is `open` / `target_exit` / `stop` / `tp` / `trailing` /
`maxhold`. `fill_hash` lets you audit dedup (no hash should appear
twice as an open).

## Honest limitations

- Paper fills assume full fills at the target's price — real
  execution would face slippage/partial fills, especially right after
  a whale's entry moves the book.
- Copying is same-run, not same-block: on a 30-min cadence we mirror
  the *position*, not the *latency edge*. This tests target selection
  + exits, not speed.
- 3–4 days is a short sample; judge expectancy, not one good/bad day.
- Scoring uses the target's reported `closedPnl` when present (fees
  excluded); rankings are what matter, not absolute dollars.
- A crash between the CSV append and the state save could duplicate
  rows on the next run — the `fill_hash` column makes this auditable;
  reruns otherwise dedup cleanly.

## Cron

Do not run manually alongside cron (two writers could interleave CSV
rows). Suggested line (every 30 minutes):

```
*/30 * * * * /usr/bin/python3 /home/hatch/workspace/copy-trading/paper_tracker.py
```

The script logs to `paper_tracker.log` itself; no redirect needed.
A run completes in well under 5 minutes for a handful of targets.
