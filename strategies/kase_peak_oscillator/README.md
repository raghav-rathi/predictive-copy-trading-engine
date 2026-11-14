# Kase Peak Oscillator

Kase Peak Oscillator / KaseCD (Cynthia Kase, "Trading with the
Odds", 1996).

- **Log returns:** r = ln(C / C[1])
- **σ_n:** stddev of r over n bars
- **KSDI_up(n)** = ln(H / min(L, n)) / σ_n
- **KSDI_dn(n)** = ln(L / max(H, n)) / σ_n
- **PeakOsc** = mean over n in {5, 10, 15, 20, 25, 30, 35, 40, 45,
  50} of (KSDI_up(n) − KSDI_dn(n))
- **KaseCD** = PeakOsc − SMA(PeakOsc, 9)
- **PeakMax** = max(2 × rolling-100 stddev of PeakOsc, 90th
  percentile of |PeakOsc| over rolling 250)
- **PeakMin** = min of the same two quantities
- **Long:** KaseCD crosses above 0 while PeakOsc < PeakMax
- **Short:** KaseCD crosses below 0 while PeakOsc > −PeakMax
- **Exit:** the opposite KCD cross, or PeakOut — PeakOsc was above
  PeakMax and has pulled back inside it (exit long); mirror for
  short
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 150-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: KSDI horizons 5–50 step 5, KCD SMA 9, PeakMax/Min
windows 100/250, 90th percentile. WARMUP=310 (see below).

Usage:

```python
from strategies.data import fetch_candles
from strategies.kase_peak_oscillator import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the warmup correction and the KCD-SMA sweep.

Sources: Kase PeakOuts —
https://www.kaseco.com/support/articles/PeakOuts_and_Permissions.pdf ;
Kase Studies (LuxAlgo) —
https://www.luxalgo.com/library/concept/kase-studies/

## Honest caveats — read before trusting this engine

- **PeakOsc is non-negative by construction.** ln(H / min L) ≥ 0
  and ln(L / max H) ≤ 0, so KSDI_up − KSDI_dn ≥ 0 and PeakOsc ≥ 0
  always (verified in tests; mean ≈ 10.0, sd ≈ 2.0 on the batch
  window). The PeakOsc level itself never crosses zero — the
  zero-crossing signal lives entirely in KaseCD (PeakOsc minus
  its own 9-bar SMA). That is the design as published, but it has
  two consequences:
  - The short-side PeakMax filter (`PeakOsc > −PeakMax`) is
    vacuous — it is true on every bar. Every KCD cross-down is a
    short entry.
  - The mirror short PeakOut (PeakOsc below −PeakMax, then back
    inside) **cannot fire**. The effective short exit is the
    opposite KCD cross alone. PeakMin is computed and exposed
    (0 ≤ PeakMin ≤ PeakMax) but is not used by the shipped
    signals.
- **KaseCD whipsaws violently on 1h bars.** KCD sd ≈ 1.2 against a
  mean of ~0, so it crosses zero every few bars: 1,311–1,365
  trades per coin over 7 months (~6/day/coin). Kase designed this
  for daily bars; on 1h the signal is mostly noise, and the
  backtest is deeply negative on all three coins (see BACKTEST.md).
- **Warmup correction:** the brief specified warmup 260, but
  PeakOsc needs 51 bars before the rolling-250 percentile window
  even starts, so PeakMax first forms at ~bar 299. WARMUP is
  310; see CALIBRATION.md.
