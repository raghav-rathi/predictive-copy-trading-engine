# POC Migration

Rolling volume-profile Point of Control (POC) trend-following.

## Mechanism

For each bar, the profile window is the last 50 bars. The window's price
range (min low to max high) is split into 20 equal bins; each bar's
volume is assigned to the bin containing its close, and the POC is the
centre of the highest-volume bin (ties: lowest bin). The POC is thus the
price where the most business was done over the last ~2 days — a
volume-weighted "fair value" level that migrates as the window rolls.

## Entry / exit

- **Long entry:** POC has risen vs 10 bars ago AND close > POC.
- **Short entry:** POC has fallen vs 10 bars ago AND close < POC.
- **Exit:** POC direction flips vs 10 bars ago (the risk layer adds a
  2xATR stop, a 2.5xATR trail, and a 120-bar max hold).

The trade thesis is migration, not reversion: a POC drifting up with
price above it is read as value being accepted higher, not as price
stretched away from value.

## Source

- Volume Profile / Point of Control explainer (POC = the price with the
  most traded volume in the window):
  https://markettrace.ai/blog/volume-profile-trading
  (verified; used for the POC definition only — the migration rule
  itself is this strategy's own construction, not the source's.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1% equity
risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
longs and shorts allowed. WARMUP = 65 bars (50-bar window + 10-bar lag
+ 5 margin).

## Honest limitation

Bin assignment uses each bar's close, not tick-level volume-at-price:
a bar whose range spans several bins contributes all its volume to one
bin. On 1h bars with wide ranges this smears the true profile. Worse,
the POC is a step function of a rolling window — it jumps when a heavy
bar enters or leaves the window — so "POC direction" flips often and
the strategy overtrades (see BACKTEST.md: 1,387 trades). Treat the POC
here as a coarse proxy, not a true volume profile.
