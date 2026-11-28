# AO Saucer (Bill Williams) — Calibration

Strict/relaxed and exit-rule sensitivity on the same
Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, pinned
batch-49 window 2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC,
6,185 bars BTC/ETH, 6,183 HYPE; same costs/sizing, 2xATR
stop, 3xATR trail, 96-bar max hold). The sweeps re-run
`add_signals(df, strict=X)` / `add_signals(df,
exit_mode=X)` -- everything else stays fixed.

## (a) Strict vs relaxed saucer (exit fixed at zero-cross)

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| Strict (shipped) | BTC | 205 | 27.3% | -$2,703 | -1.81 | 0.70 | -$13.18 |
| Strict (shipped) | ETH | 218 | 32.6% | -$906 | -0.42 | 0.90 | -$4.15 |
| Strict (shipped) | HYPE | 190 | 31.6% | -$1,221 | -0.59 | 0.87 | -$6.42 |
| Strict (shipped) | **Combined** | **613** | **30.5%** | **-$4,829** | **-1.27** | **0.83** | **-$7.88** |
| Relaxed | BTC | 205 | 27.3% | -$2,703 | -1.81 | 0.70 | -$13.18 |
| Relaxed | ETH | 218 | 32.6% | -$906 | -0.42 | 0.90 | -$4.15 |
| Relaxed | HYPE | 190 | 31.6% | -$1,221 | -0.59 | 0.87 | -$6.42 |
| Relaxed | **Combined** | **613** | **30.5%** | **-$4,829** | **-1.27** | **0.83** | **-$7.88** |

The two variants are identical to the dollar -- not a
coincidence and not a bug. The relaxed rule drops only the
ao[i-2] > 0 requirement, but the turn condition
ao[i-1] < ao[i-2] together with ao[i-1] > 0 forces
ao[i-2] > 0 anyway (mirror for sells). The "relaxed"
condition can never fire where strict does not, so this
sweep is degenerate by construction. It is reported anyway
because the brief asked for it, and the test
(`test_relaxed_strict_identical`) pins the identity on
random data. There is no looser saucer to ship here --
loosening would mean dropping the ao[i-1] > 0 requirement,
which is a different setup (a saucer straddling zero).

## (b) Exit rule (strict saucer fixed)

| Exit | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| Zero-cross (shipped) | BTC | 205 | 27.3% | -$2,703 | -1.81 | 0.70 | -$13.18 |
| Zero-cross (shipped) | ETH | 218 | 32.6% | -$906 | -0.42 | 0.90 | -$4.15 |
| Zero-cross (shipped) | HYPE | 190 | 31.6% | -$1,221 | -0.59 | 0.87 | -$6.42 |
| Zero-cross (shipped) | **Combined** | **613** | **30.5%** | **-$4,829** | **-1.27** | **0.83** | **-$7.88** |
| Two consecutive adverse AO bars | BTC | 365 | 28.8% | -$4,946 | -4.80 | 0.49 | -$13.55 |
| Two consecutive adverse AO bars | ETH | 360 | 29.4% | -$3,206 | -2.23 | 0.69 | -$8.90 |
| Two consecutive adverse AO bars | HYPE | 329 | 37.7% | -$973 | -0.69 | 0.90 | -$2.96 |
| Two consecutive adverse AO bars | **Combined** | **1,054** | **31.8%** | **-$9,125** | — | **0.69** | — |

## One-line verdict

- **Strict = relaxed:** identical by proof, combined -$4,829
  on 613 trades. No choice to make.
- **Zero-cross exit (shipped):** combined -$4,829 on 613
  trades.
- **Two-bar adverse exit:** combined -$9,125 on 1,054
  trades -- nearly twice the loss. Exiting on two red AO
  bars chops winners early and, worse, frees the slot to
  re-enter the next saucer sooner, so trade count nearly
  doubles and fees ($6,699 vs $4,282) do the extra damage.
  BTC collapses to PF 0.49. The earlier exit is strictly
  worse on every coin except HYPE, where it is still a
  loser.
- **Shipped decision:** keep strict saucer + zero-cross
  exit as the registry config regardless. Both were fixed
  before any backtest was run; the sweeps are diagnostic
  only. No swept variant is profitable, so there is nothing
  to tune toward -- the edge is absent, not mis-parameterized.
  Do not ship the two-bar exit on the strength of its HYPE
  number.

## Audit

- **Lookahead audit:** no lookahead found. AO is the
  difference of two trailing SMAs; the saucer test reads
  only ao[i-2..i]; exits are crossed_above / crossed_below
  on AO vs zero or opposite-saucer flags. The truncation
  test (`test_no_lookahead_truncation`) confirms indicator
  and signal values at bar j are identical whether computed
  on the full frame or on the frame truncated at j.
- **Source check:** the saucer construction (AO = SMA(5) −
  SMA(34) of median price; buy = red-then-green turn above
  zero, sell = mirror) matches the cited Williams source.
  Two documented choices: trading the completion bar rather
  than waiting for a confirming bar, and the zero-cross
  exit (Williams' own exit guidance is the opposite saucer
  / AO direction change, which the signal exit covers).
- **Tests:** 19/19 pass (`python3 -m unittest
  strategies.ao_saucer.test_ao_saucer`).
- **No parameter was tuned to PnL.** AO lengths stay 5/34,
  exit stays zero-cross.
