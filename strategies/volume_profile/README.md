# Volume Profile Value-Area Fade

Fades **failed auctions** at the edges of a rolling composite volume
profile: when price breaks out of value and immediately comes back,
the auction failed and price tends to rotate back across value.

## Mechanism

1. **Rolling profile**: trailing 168 bars, 24 equal price bins spanning
   the window's `[min low, max high]`. Each bar's volume is spread
   uniformly over the bins its `[low, high]` range touches (causal —
   only bars ≤ i).
2. **POC** = max-volume bin.
3. **Value area**: expand outward from the POC, each step adding the
   adjacent bin with the most volume, until ≥ 70% of the window's
   volume is captured. `VAH` = top edge of the highest VA bin,
   `VAL` = bottom edge of the lowest VA bin.
4. **Entry**: long when the prior bar's close dipped below VAL and the
   current bar closes back above it (failed breakdown); short when the
   prior close spiked above VAH and the current close falls back below
   (failed breakout). VAL/VAH are taken from the prior bar's profile so
   the trigger level is known before the entry bar closes.
5. **Exits**: none from the signal side. Risk config: 2xATR stop,
   3xATR target (a proxy for the full VAL→VAH rotation), 120-bar max
   hold, no trailing.

## Parameters

| Param | Value |
|---|---|
| Profile window | 168 bars |
| Bins | 24 |
| Value-area coverage | 70% of window volume |
| Stop / target | 2.0 / 3.0 × ATR(14) |
| Max hold | 120 bars |
| Sizing | 1% risk/trade, 3× leverage cap |

## Usage

```python
from strategies.volume_profile import indicators, risk, signals

ind = indicators.add_indicators(df)   # OHLCV with t,o,h,l,c,v
sig = signals.add_signals(ind)
from strategies.backtest import run_backtest
res = run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                   use_funding=False)
print(res.metrics())
```

## Source

Volume profile POC/VAH/VAL —
https://markettrace.ai/blog/volume-profile-trading
