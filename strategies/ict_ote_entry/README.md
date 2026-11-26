# ICT Optimal Trade Entry (OTE)

ICT's Optimal Trade Entry: a liquidity sweep of a 20-bar swing
extreme, an impulsive displacement that breaks market
structure, then entry on the retracement into the 62-79%
OTE zone of the leg (70.5% midline). The sweep takes the
stops; the displacement proves the move is real; the OTE
zone is where the smart money is supposed to re-enter.

- **Sweep:** close beyond the prior 20-bar swing extreme
  (below the low for a long, above the high for a short),
  then close back inside that level within 3 bars of the
  bar that made the sweep extreme
- **Displacement:** within the next 6 bars, price moves
  >= 1.5x ATR(14) in the sweep-opposite direction (from the
  back-inside close) AND breaks the near swing (frozen at
  the back-inside bar)
- **Leg:** sweep extreme -> displacement extreme (highest
  high / lowest low from the back-inside bar through the
  confirmation bar); the zone is fixed at confirmation and
  is not redrawn if price extends further
- **Long:** close retraces into the OTE zone (62-79% of the
  leg) after a bullish displacement
- **Short:** mirror
- **Invalidation:** close beyond 100% of the leg (beyond the
  sweep extreme) cancels a pending setup; a setup expires
  if the zone is not touched within 24 bars of the
  displacement extreme
- **Exit:** close beyond the sweep extreme, or the opposite
  setup's entry; 2xATR hard stop, 3xATR trail, 120-bar max
  hold behind them
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: swing 20 bars, displacement 1.5x ATR(14),
OTE zone 62-79% (midline 70.5%), back-inside 3 bars,
displacement window 6 bars, setup expiry 24 bars. Swing
extremes are judged on prior bars (shifted by 1); the near
swing broken by the displacement is frozen at the
back-inside bar -- a rolling level would absorb the
displacement itself and a gradual move could never break
it.

Deviation from ICT, documented: ICT places the stop beyond
the leg start (the sweep extreme). Here the house 2xATR
stop replaces that structural stop -- the sweep extreme is
still used as the signal exit and the pending-setup
invalidation, not as the stop level.

Sources: ICT Optimal Trade Entry --
https://tradingdocs.vercel.app/en/ict/ote and
https://orderblock.net/ict/optimal-trade-entry

Usage:

```python
from strategies.ict_ote_entry import indicators, signals, risk

df = indicators.add_indicators(df)  # disp_mult=1.5 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the displacement-threshold 1.0/1.5/2.0
sensitivity check.
