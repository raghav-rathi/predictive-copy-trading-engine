# Mitigation Block

ICT mitigation block: a failed order block after a failure swing.
Price makes a swing, pulls back, rallies to a LOWER high that never
trades through the prior high — the failed rally — then breaks the
pullback low. The candle that launched the failed rally becomes
the block, and the first return into it is the entry.

## Rules

- **Bearish:** swing high H1, pullback swing low L1, rally to a
  LOWER high H2 (H2 < H1; the prior high is never traded through),
  then a close below L1 (structure break). Block = the candle at
  the L1 centre, zone [low, high] of that candle.
- **Bullish (mirror):** swing low L1, bounce to swing high H1,
  drop to a HIGHER low L2 (never trades through L1), close above
  H1. Block = the candle at the H1 centre.
- **Short entry:** the first close inside the armed bearish block
  after the break.
- **Long entry:** the first close inside the armed bullish block
  after the break.
- **Long exit:** an opposite bearish-block signal OR a close below
  the bullish block's low.
- **Short exit:** an opposite bullish-block signal OR a close
  above the bearish block's high.
- **Block expiry:** 150 bars after the break. Only the most recent
  block per side is active; a newer break replaces an armed block.
- A close through the block (above a bearish block's high / below
  a bullish block's low) clears it, entered or not — before entry
  that is a blown-through block, after entry it is the exit.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

Swings are causal 5-bar pivots: a swing high at centre j iff
h[j] is the max of h[j-2..j+2], recorded at the confirmation bar
(centre+2), never at the centre bar.

This is distinct from `breaker_block` (which requires a SWEEP of
the prior extreme first — price trading through it before the
block flips polarity) and from `order_block_retest` (a fresh
block, no failure swing): here the defining feature is the
failure swing that never reaches the prior extreme, then the
structure break. All computation is causal.

## Sources

- The Right Trader, "Mitigation Block":
  https://therighttrader.com/learn/smart-money-concepts/mitigation-block

## Files

- `indicators.py` — pivot + failure-swing state machines, blocks
- `signals.py` — entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_mitigation_block.py` — 19 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m unittest strategies.mitigation_block.test_mitigation_block -v
python3 strategies/mitigation_block/run_backtest.py
```

Paper only, no live execution.
