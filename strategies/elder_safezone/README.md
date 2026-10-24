# Elder SafeZone

Trade Alexander Elder's SafeZone system from *Come Into My
Trading Room* (2002): a volatility-based trailing stop line
that hangs below the recent lows in an uptrend (mirrored above
the highs in a downtrend). The line is not a fixed ATR multiple
off price — it adapts to how deep recent pullbacks actually
penetrated:

- **SafeZone long** = highest low of the last 10 bars −
  2.5 × average counter-trend penetration, where penetration on
  a bar = max(0, previous low − this low).
- **SafeZone short** = lowest high of the last 10 bars +
  2.5 × average upward penetration (mirror).

The logic: in a healthy uptrend, pullbacks penetrate the prior
low only shallowly, so the average penetration is small and the
line hugs the lows. When a bar closes below the line, the
counter-trend move is deeper than anything normal for the last
10 bars — the trend is suspect, and the trade exits.

## Entries

- **Long:** close crosses *above* EMA(22) AND close is above
  the SafeZone long line. The EMA cross is the trend trigger;
  the SafeZone condition keeps the entry honest — a cross that
  prints while price is already below its own stop line is a
  dead-cat bounce off a broken trend, not a new trend.
- **Short:** exact mirror — cross below EMA(22) while below
  the SafeZone short line.

## Exits

The SafeZone breaks themselves, no EMA condition — once the
trade is on, the line is the arbiter:

- **long_exit:** close below the SafeZone long line
- **short_exit:** close above the SafeZone short line

## Risk

2.0xATR hard stop and 2.5xATR chandelier trail sit *behind* the
SafeZone line as catastrophe backstops (the line is the primary
exit), no fixed target, 96-bar (~4-day) max hold — a SafeZone
trend trade that hasn't resolved in four days is chop, not
trend. 1% risk/trade, 3x leverage cap, long/short symmetric.

Parameters: EMA 22, SafeZone window 10, penetration multiple
2.5. All fixed a priori; no optimization. WARMUP=60.

Usage:

```python
from strategies.elder_safezone import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results
and CALIBRATION.md for the a-priori calibration rationale.

Sources:

- Elder SafeZone mechanics —
  https://www.incrediblecharts.com/indicators/safezone.php
- Alexander Elder, *Come Into My Trading Room* (2002)
