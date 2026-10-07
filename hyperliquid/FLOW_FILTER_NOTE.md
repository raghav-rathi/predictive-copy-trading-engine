# Uncopyable-Flow Filter — iteration note

**Date:** 2026-10-07
**Status:** implemented, tested, live in paper tracker scoring path

## Thesis

Not all profitable-looking flow is copyable. From open-source
copy-trading research (lindagrey/hyperliquid-copy-trader wallet
heuristics; tradingstrategy-ai HFT identification metrics; xlev-v's
"do NOT copy HFT / market makers / scalpers"):

- **HFT**: fill rates a 30-min polling copier cannot keep up with —
  the copy bleeds on latency/slippage.
- **Scalpers**: average hold shorter than our poll interval — the edge
  decays before the copy lands.
- **Market makers**: long AND short open simultaneously on the same
  coin — mirroring both sides is a guaranteed loss.
- **Chronic flippers**: constant direction reversals — the copy
  arrives after the edge is gone.

A flagged wallet is forced to `"pass"` (never copy **and** never fade —
fading an HFT book has the same latency problem in reverse).

## What was built

- `hyperliquid/flow_filter.py`: `dedup_fills` (fragment aggregation),
  `flow_metrics`, `detect_uncopyable`, `is_uncopyable`.
- Wired into `hyperliquid/scorer.py`: `score_wallet` attaches
  `flow_flags`/`flow_metrics`; `classify(..., flow_flags=...)` forces
  pass on any flag. `paper_tracker.py` passes the flags through.
- Config: optional `hyperliquid.flow_filter` section (defaults are the
  documented behavior when absent).

## Calibration findings (the interesting part)

1. **Fill fragmentation is massive.** One market order sweeping the
   book prints up to 22 fill records at the same millisecond (Aaroh:
   991 fills = 232 parent orders). Counting raw fills flagged 12/15
   live targets as "HFT" — pure artifact. The filter aggregates by
   (timestamp, coin, dir) first.
2. **Thresholds are derived from our poll loop, not tuned to data:**
   scalper = avg hold < 1800s (our 30-min poll interval); HFT =
   >30 parent orders/hr sustained or 3+ distinct 100-order burst
   hours (a single busy hour is a rebalance, not a structure).
3. **Latent bug found:** `scorer.HyperliquidInfo._post` used
   `json.load` on a decoded string (should be `json.loads`) — the
   `score_address` CLI path was broken; the paper tracker never hit
   it because it has its own fetch.

## Empirical result (2026-10-07)

Ran the filter over trailing-30d fills for all 15 live paper targets:

**0/15 flagged.** No HFT, no scalpers (shortest avg hold: 15h),
no market makers, no chronic flippers.

Reading: the current book's underperformance is not a flow-mechanics
problem — all 15 targets are structurally copyable. The filter stands
as a conservative guardrail for future target admissions (it will
catch the toxic flow the day it shows up).
