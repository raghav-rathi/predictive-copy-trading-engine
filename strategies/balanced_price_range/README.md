# Balanced Price Range

ICT Balanced Price Range (BPR): where a bullish and a bearish fair
value gap overlap, price tends to respect the overlap zone. This
strategy trades the return into that overlap — not a single gap.

## Rules

- **Fair value gap (FVG), confirmed at bar i from bars i-2 and i:**
  bullish iff low[i] > high[i-2], gap [high[i-2], low[i]];
  bearish iff high[i] < low[i-2], gap [low[i], high[i-2]].
- **BPR formation:** a bullish and a bearish FVG overlap in price
  AND the second forms within 60 bars of the first. Direction =
  direction of the LATER gap; zone = the overlap [max of the two
  gap bottoms, min of the two gap tops]. Only the most recent BPR
  per side is active; a newer BPR on the same side replaces it.
- **Long entry (bullish BPR):** the first close inside the zone
  after price had closed above the zone (a return into it).
- **Short entry (bearish BPR):** the first close inside the zone
  after price had closed below the zone.
- **Long exit:** an opposite bearish-BPR signal OR a close below
  the bullish zone's bottom (invalidation).
- **Short exit:** an opposite bullish-BPR signal OR a close above
  the bearish zone's top (invalidation).
- **Expiry:** a zone expires 100 bars after formation, or once
  price closes through it (close below a bullish zone's bottom /
  above a bearish zone's top invalidates it). Each zone enters once.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

This is distinct from `fvg_mitigation` (single FVG): the overlap
of TWO opposite gaps is the whole point here — a lone gap never
forms a BPR, and the entry requires the return into the overlap
after trading beyond it. All computation is causal: gaps are
recorded at their confirmation bar, never earlier.

## Sources

- Inner Circle Trader, "ICT Balanced Price Range (BPR)":
  https://innercircletrader.net/tutorials/ict-balanced-price-range-bpr/
- ICT Terminal, "Balanced Price Range (BPR) — Overlapping Fair
  Value Gaps":
  https://chart.iccterminal.trade/blog/balanced-price-range-bpr-overlapping-fair-value-gaps.html

## Files

- `indicators.py` — FVG detection + BPR formation/tracking
- `signals.py` — entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_balanced_price_range.py` — 19 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m unittest strategies.balanced_price_range.test_balanced_price_range -v
python3 strategies/balanced_price_range/run_backtest.py
```

Paper only, no live execution.
