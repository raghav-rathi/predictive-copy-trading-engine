# Ehlers Center of Gravity

John Ehlers' Center of Gravity oscillator ("Rocket Science for
Traders", 2001): a near-zero-lag oscillator built as the balance
point of prices over a window, traded here on its crosses with a
3-bar SMA trigger line.

## Rules

- **CG:** over a trailing 10-bar window of closes p[0..9] (p[0]
  oldest), CG = -sum((i+1) * p[i] for i in 0..9) / sum(p[i]).
- **Trigger:** SMA(3) of CG.
- **Long entry:** CG crosses up through trigger (transition only).
- **Short entry:** CG crosses down through trigger (transition only).
- **Long exit:** CG crosses down through trigger.
- **Short exit:** CG crosses up through trigger.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars (CG first defined at bar 9, trigger at bar 11).

All computation is causal: rolling windows are trailing, and the
cross uses bars through the current close only.

**Convention warning:** the brief's formula weights the most recent
price most heavily (weight 10) and the oldest least (weight 1),
with an overall negative sign. That is the reverse of Ehlers'
original paper, where the most recent price has weight 1. With the
brief's convention CG moves opposite to price, so a "long on cross
up" fires as prices fall. Implemented exactly as specified — see
CALIBRATION.md for the full note.

## Sources

- John Ehlers, "The CG Oscillator" (Mesa Software):
  https://mesasoftware.com/papers/TheCGOscillator.pdf
- John Ehlers, "Rocket Science for Traders" (Wiley, 2001), Chapter 1.

## Files

- `indicators.py` — CG and its 3-bar trigger
- `signals.py` — CG/trigger cross entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_center_of_gravity.py` — 16 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/center_of_gravity/test_center_of_gravity.py -q
python3 strategies/center_of_gravity/run_backtest.py
```

## Verdict

Heavy loser: -$20,893.09 combined on 3657 trades (PF 0.70,
Sharpe -8.32, MaxDD -69.9%). The CG whipsaws across its 3-bar
trigger constantly at 1h frequency; gross PnL before fees is about
-$2,364 and $18,529 of fees does the rest. No edge on this window —
see BACKTEST.md.

Paper only, no live execution.
