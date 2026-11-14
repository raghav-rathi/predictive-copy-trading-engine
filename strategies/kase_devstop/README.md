# Kase DevStop

Cynthia Kase's volatility stop from *Trading with the Odds* (1996) —
a trailing stop built from the two-bar true range, so it sits far
enough out to survive normal noise but tight enough to cut a real
reversal. The stop line is both the entry trigger and the exit.

- **DTR** = max(H_t, H_{t−1}) − min(L_t, L_{t−1}) — the two-bar true
  range, which catches the gap/extension a one-bar range misses
- **Band** = mean(DTR, 30) + 1.0 × stddev(DTR, 30) (sample stddev,
  ddof=1) — Kase's published default
- **Long stop** = ratchet_up(highest high since flip − band) — the
  stop only ever moves up while long
- **Short stop** = ratchet_down(lowest low since flip + band) — the
  stop only ever moves down while short
- **Flip long:** close crosses above the short-stop line;
  **flip short:** close crosses below the long-stop line
- **Entry:** on the flip. **Exit:** the DevStop line itself — there
  is no separate exit rule
- **Risk:** the harness RiskConfig is deliberately set WIDE so the
  DevStop drives exits: 6xATR(14) hard stop as a disaster backstop
  only, NO chandelier trail (a second trailing stop would fight the
  DevStop), no target, 300-bar max hold, 1% risk/trade, 3x leverage.
  Sizing uses the 6xATR stop distance, so positions run smaller than
  a 2xATR strategy's — that is the price of the wide backstop.

Parameters: DTR window 30, band std multiplier 1.0. WARMUP=60
(DTR(30) band spin-up, with margin).

Initial-state convention (documented, not a trade): at the first bar
with a valid band the tracker starts in the long state with the stop
set from that bar's high. No entry signal is emitted for the initial
state — the first trade only fires on a genuine flip.

Usage:

```python
from strategies.data import fetch_candles
from strategies.kase_devstop import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the band-multiplier sensitivity check.

Sources: https://docs.wickra.org/Indicators/Indicator-KaseDevStop
and https://www.luxalgo.com/library/concept/kase-studies/
