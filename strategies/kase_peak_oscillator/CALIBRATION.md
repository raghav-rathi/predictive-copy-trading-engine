# Kase Peak Oscillator — Calibration

## Shipped parameters (a priori, from Kase 1996)

KSDI horizons {5, 10, 15, 20, 25, 30, 35, 40, 45, 50}, KCD SMA 9,
PeakMax/Min windows 100/250 with the 90th percentile, σ_n =
stddev of log returns (pandas rolling std, ddof=1). None were
chosen from the backtest. The shipped setting is the published
default throughout.

## Spec correction 1: warmup 260 → 310

The brief specified warmup 260. That undercounts: PeakOsc needs
51 bars (the n=50 KSDI leg) before the rolling-250 percentile
window even starts, so PeakMax first forms at ~bar 299
(51 + 249 − 1) and is NaN before that. WARMUP is therefore 310.
With warmup 260 the harness would have allowed entries from bar
260 while the long filter (`PeakOsc < PeakMax`) was still NaN —
harmless in practice (NaN comparisons are False, so no entries
fired before bar ~299 anyway), but 310 is the honest warmup and
is what the backtest ran with. Tests assert PeakMax is NaN
through bar 298 and formed from bar 310.

## Spec correction 2 (documented, not changed): PeakMin unused

PeakMin = min(2× rolling-100 stddev, 90th pct) is computed and
exposed, but the brief's signals never use it, and the mirror
short PeakOut as literally specified (PeakOsc below −PeakMax)
cannot fire because PeakOsc ≥ 0. I shipped the literal spec and
documented the consequence in README.md rather than inventing a
PeakMin-based short PeakOut the brief did not ask for.

## KCD-SMA sweep (sensitivity only — shipped SMA stays 9)

Same signals/risk, KCD SMA 5 / 9 (shipped) / 21, Hyperliquid 1h
BTC/ETH/HYPE over the batch window, warmup 310:

| KCD SMA | BTC | ETH | HYPE | Combined |
|---|---|---|---|---|
| 5 | 1,703t, -$9,303 | 1,709t, -$8,702 | 1,642t, -$6,574 | 5,054t, -$24,579 |
| 9 (shipped) | 1,365t, -$8,711 | 1,339t, -$7,944 | 1,311t, -$5,819 | 4,015t, -$22,474 |
| 21 | 954t, -$7,969 | 946t, -$7,137 | 895t, -$4,410 | 2,795t, -$19,517 |

Slowing the CD helps monotonically (fewer whipsaw crosses, smaller
losses) but does not rescue the strategy: SMA 21 still loses
−$19,517 combined with win rates 36–43%. The direction is
informative — the 9-bar CD is too fast for 1h bars — but leaning
toward SMA 21 *because* it loses least on this window would be
in-sample selection on a still-deeply-negative result. Shipped
setting stays the published SMA 9. If this engine is ever
revisited, the experiment to run is a daily-bar version, not a
slower hourly CD.

## Implementation notes

- Early versions averaged the ten KSDI legs with pandas'
  default skipna mean, so PeakOsc was "formed" from bar 5 using
  only the short horizons, and PeakMax with a skipna max was
  formed from bar ~104 using only the stddev leg. Both now
  require all legs / both quantities (explicit all-non-NaN mask
  for the mean; `np.maximum`/`np.minimum`, which propagate NaN,
  for PeakMax/PeakMin). PeakOsc first forms at bar 50, PeakMax
  at bar ~299; tests assert both.
- Formula checks in tests: KCD ≡ PeakOsc − SMA(PeakOsc, 9)
  exactly; PeakMax ≡ max(2σ100, p90_250) exactly; PeakOsc ≥ 0 on
  all non-NaN bars; 0 ≤ PeakMin ≤ PeakMax.
- Diagnostics on the batch window: PeakOsc mean ≈ 10.0, sd ≈
  2.0; KCD sd ≈ 1.2; PeakMax mean ≈ 12.5; PeakOsc exceeds
  PeakMax on ~10% of bars.
