# VPIN Toxicity Exhaustion

An experimental exhaustion read of the academic **VPIN** (Volume-Synchronized
Probability of Informed Trading) metric from Easley, López de Prado, and
O'Hara.

## Mechanism

1. **Bulk Volume Classification** per 1h bar: `buyV = v·(c−l)/(h−l)`
   (`sellV = v − buyV`); a flat bar (`h == l`) splits 50/50.
2. **Volume buckets**: bars accumulate into buckets of size
   `V = trailing 50-bar mean volume` (recomputed causally per bar).
   A bar that overflows a bucket is split proportionally and the
   remainder carries forward.
3. **VPIN** = mean of `|buy−sell|/bucket` over the last 50 completed
   buckets; **percentile** = rolling rank of VPIN over the trailing
   252 bars (shifted, causal).
4. **Entry**: VPIN percentile > 0.90 **and** the close makes a new
   20-bar low → long (panic exhaustion: toxic flow absorbed, move
   spent). Symmetric on new 20-bar highs → short.
5. **Exits**: none from the signal side. The risk config manages the
   trade: 2xATR stop, 2xATR target, 48-bar max hold, no trailing.

## Parameters

| Param | Value |
|---|---|
| Bucket volume span | 50 bars (causal mean) |
| Buckets in VPIN | 50 |
| VPIN percentile span | 252 bars |
| Toxicity trigger | percentile > 0.90 |
| Panic lookback | 20 bars |
| Stop / target | 2.0 / 2.0 × ATR(14) |
| Max hold | 48 bars |
| Sizing | 1% risk/trade, 3× leverage cap |

## Usage

```python
from strategies.vpin import indicators, risk, signals

ind = indicators.add_indicators(df)   # OHLCV with t,o,h,l,c,v
sig = signals.add_signals(ind)
from strategies.backtest import run_backtest
res = run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                   use_funding=False)
print(res.metrics())
```

## Source

VPIN (Easley/de Prado/O'Hara) —
https://jheusser.github.io/2013/10/13/informed-trading.html
