# Fibonacci Cluster

Fibonacci confluence zones: trade the bounce off a price zone where
retracement levels from different swings stack up.

- **Swings:** ZigZag from 5-bar fractal pivots (a high pivot is the
  max high of h[i-2..i+2], a low pivot the min low). A pivot centred
  on bar i is only confirmed at bar i+2 — no lookahead. Pivots must
  alternate high/low and move ≥ 2% from the last pivot; a
  same-type pivot replaces the last only if more extreme.
- **Levels:** 38.2% / 50% / 61.8% retracements of the last 3
  completed swings. Up swing (low → high): levels below the high.
  Down swing (high → low): levels above the low.
- **Cluster:** ≥ 2 levels from different swings within 0.5x ATR(14)
  of each other; cluster price = mean of member levels. The nearest
  cluster below the close is the support cluster, the nearest above
  is the resistance cluster.
- **Long:** the low touches the support cluster (within 0.25x ATR)
  and the bar closes back above it, after the previous close was
  still above the cluster (a genuine dip-and-bounce, not a reclaim)
- **Short:** the high touches the resistance cluster (within 0.25x
  ATR) and the bar closes back below it, after the previous close
  was still below it
- **Exit:** touch of the opposite cluster with the same bounce
  logic (a long exits on a resistance-cluster tap that closes back
  below it)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 200-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: 5-bar fractal pivots, min swing 2%, levels 38.2/50/61.8,
cluster width 0.5x ATR(14), touch 0.25x ATR(14). WARMUP=120.

Clusters form readily at the shipped 0.5x ATR width (on 86–90% of
bars per coin), so no width relaxation was needed.

Usage:

```python
from strategies.data import fetch_candles
from strategies.fibonacci_cluster import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the cluster-width sensitivity check.

Source: Fibonacci confluence / clusters —
https://www.fxfoundations.com/learn/technical-analysis/fibonacci

## Honest caveats

- Fibonacci levels have no physical law behind them; a cluster is
  an order-clustering hypothesis (many watchers at the same price),
  not a guarantee — and with 9 levels per bar, *some* level is
  almost always nearby, so "confluence" is cheap to find.
- The nearest cluster is often very close to the close, so the
  0.25x ATR touch test fires on ordinary noise — this is a
  high-frequency mean-reversion system (961 trades in 7 months),
  and fees ($6,048) are a major line item.
- Swing endpoints are confirmed pivots, but a same-type pivot can
  still supersede the last pivot and shift a cluster mid-swing;
  levels are live estimates, not fixed lines.
