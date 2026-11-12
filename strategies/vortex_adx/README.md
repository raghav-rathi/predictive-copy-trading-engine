# Vortex + ADX

The Vortex indicator (Etienne Botes & Douglas Siepman, *Technical
Analysis of Stocks & Commodities*, January 2010) measures upward and
downward directional movement as two lines, VI+ and VI-, each the
smoothed vortex movement normalised by smoothed true range. When VI+
crosses above VI-, upward momentum is dominant; the mirror cross
marks downward dominance. The indicator is unreliable in sideways
markets, so this build adds the standard confirmation: only take a
cross when ADX(14) > 25 (a real trend is present), and exit when the
trend fades (ADX(14) < 20) or the opposite cross fires.

## Rules

- **Long entry:** VI+ crosses above VI- with ADX(14) > 25.
- **Short entry:** VI- crosses above VI+ with ADX(14) > 25.
- **Long exit:** the opposite VI cross, or ADX(14) < 20.
- **Short exit:** the opposite VI cross, or ADX(14) < 20.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the signal exit. Max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Etienne Botes & Douglas Siepman, "The Vortex Indicator",
  *Technical Analysis of Stocks & Commodities*, Vol. 28:1 (Jan 2010): https://capital.com/en-eu/learn/technical-analysis/vortex-indicator

Paper only, no live execution.
