# DeMark Range Expansion Index (TD REI)

DeMark's Range Expansion Index: an oscillator on the signed high/low
momentum versus two bars earlier, bounded to [−100, +100].

## Formula

Per bar t (DeMark, *The New Science of Technical Analysis*, 1994, ch. 4):

- `high_mom = H_t − H_{t−2}`, `low_mom = L_t − L_{t−2}`
- Gate A: `(H_t ≥ L_{t−5} or H_t ≥ L_{t−6}) and (L_t ≤ H_{t−5} or L_t ≤ H_{t−6})`
- Gate B: `(H_{t−2} ≥ C_{t−7} or H_{t−2} ≥ C_{t−8}) and (L_{t−2} ≤ C_{t−7} or L_{t−2} ≤ C_{t−8})`
- `num_t = high_mom + low_mom` if (A or B), else `0`; `den_t = |high_mom| + |low_mom|` every bar
- `REI_t = 100 × Σ(num, 5) / Σ(den, 5)` — the summation window is DeMark's canonical **5 bars**; the gate needs data 8 bars back (see CALIBRATION.md for the brief's "8-bar window" correction). NaN when the denominator sum is 0.

## Rules

- Long: REI crosses above −60 from below. Exit on REI crossing below +60.
- Short: REI crosses below +60 from above. Exit on REI crossing above −60.
- All computation is causal, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- Tom DeMark, *The New Science of Technical Analysis* (1994), ch. 4 — via the AmiBroker AFL Formula Library: https://www.amibroker.com/newsletter/02-2000.html
- Wickra TD REI reference (same formula): https://docs.wickra.org/Indicators/Indicator-TdRei

Paper only, no live execution.
