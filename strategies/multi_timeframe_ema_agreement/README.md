# Multi-Timeframe EMA Agreement filter

From BotLab, "Do Funding Rate and Open Interest Filters Improve
a Crypto Bot?" (2026-10-12): of 12 filters × 5 datasets (60
combinations, costs + funding included, point-in-time stamped,
time-split validation), this was the **only** one clearing the
multiple-testing bar (t ≈ 2.86, the expected max of 60 noise
trials): a trade is taken only when the fast and slow EMA pairs
on the 4h timeframe both point the same way as the trade.

## Mechanism

Base entry is a 1h trend cross — EMA(9) crossing EMA(21):

- **LONG** only when EMA(9) crosses above EMA(21) on 1h AND
  the 4h EMA(9) > 4h EMA(21).
- **SHORT** only when EMA(9) crosses below EMA(21) on 1h AND
  the 4h EMA(9) < 4h EMA(21).

The 4h EMAs are computed by resampling the 1h closes to 4h bars
(UTC-anchored) inside indicators.py, using **only completed 4h
bars**: the 1h bar at time t reads the 4h EMA of the most recent
4h bar whose start is ≤ t − 4h, so a 4h bar covering [T, T+4h)
first becomes visible to the 1h bar opening at T+4h. No partial
4h bar is ever read — the same point-in-time discipline the
study insists on (a filter that quietly reads the current
period's data looks brilliant and is worthless).

**Exit:** the opposite 1h cross. The 4h filter is an entry gate
only, as in the study.

## What the study found about the other filters

Funding-rate and open-interest filters added nothing: across the
cells where they applied they agreed with 84–100% of trades, and
in six of ten they were effectively constant — a filter that
never says no cannot improve anything. They are useful as risk
guardrails (stand aside in a genuinely extreme state), not as
entry signals, so none is implemented here. The long/short
account ratio helped on some datasets and hurt on others — a
dataset description, not a market fact — also not implemented.

## Risk

2xATR(14) stop, 3xATR chandelier trail, no fixed target (the
opposite cross exits), 120-bar (~5-day) max hold, 1% risk per
trade, 3x leverage cap. WARMUP = 120 bars (4h EMA(21) needs 21
completed 4h bars = 84 1h bars, plus margin).

Source: BotLab — "Do Funding Rate and Open Interest Filters
Improve a Crypto Bot?"
(https://botlab.org.uk/learn/do-funding-rate-and-open-interest-filters-improve-a-crypto-bot).
