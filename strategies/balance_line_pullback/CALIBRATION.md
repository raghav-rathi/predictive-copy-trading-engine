# Balance Line Pullback (Bill Williams) — Calibration

Touch-tolerance and mouth-gate sensitivity on the same
Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, pinned
batch-49 window 2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC,
6,185 bars BTC/ETH, 6,183 HYPE; same costs/sizing, 2xATR
stop, 3xATR trail, 96-bar max hold). The sweeps re-run
`add_indicators(df, touch_tol=X)` / `add_signals(df,
require_mouth=X)` -- everything else stays fixed.

## Touch tolerance (mouth required)

| Tolerance | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.5xATR (shipped) | BTC | 410 | 22.7% | -$5,271 | -3.45 | 0.61 | -$12.86 |
| 0.5xATR (shipped) | ETH | 446 | 22.2% | -$3,920 | -2.16 | 0.73 | -$8.79 |
| 0.5xATR (shipped) | HYPE | 398 | 27.4% | -$2,240 | -1.17 | 0.84 | -$5.63 |
| 0.5xATR (shipped) | **Combined** | **1,254** | **24.0%** | **-$11,431** | **-2.99** | **0.72** | **-$9.12** |
| 1.0xATR | BTC | 433 | 23.8% | -$5,520 | -3.58 | 0.60 | -$12.75 |
| 1.0xATR | ETH | 474 | 22.4% | -$4,876 | -2.84 | 0.66 | -$10.29 |
| 1.0xATR | HYPE | 414 | 27.1% | -$2,653 | -1.30 | 0.81 | -$6.41 |
| 1.0xATR | **Combined** | **1,321** | **24.3%** | **-$13,050** | — | — | — |

## Mouth gate (tolerance fixed at 0.5xATR)

| Mouth gate | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| Required (shipped) | **Combined** | **1,254** | **24.0%** | **-$11,431** | **-2.99** | **0.72** | **-$9.12** |
| Jaw-only (no mouth) | BTC | 723 | 18.8% | -$7,743 | -6.08 | 0.49 | -$10.71 |
| Jaw-only (no mouth) | ETH | 790 | 18.9% | -$6,511 | -4.09 | 0.65 | -$8.24 |
| Jaw-only (no mouth) | HYPE | 625 | 24.5% | -$2,311 | -0.94 | 0.87 | -$3.70 |
| Jaw-only (no mouth) | **Combined** | **2,138** | **20.5%** | **-$16,565** | — | — | — |

## One-line verdict

- **Tolerance 0.5xATR:** the shipped setting -- combined
  -$11,431 on 1,254 trades.
- **Tolerance 1.0xATR:** combined -$13,050 on 1,321 trades
  -- a wider touch band just admits more chop; worse on
  every coin.
- **Mouth required:** the shipped setting -- combined
  -$11,431. The gate earns its keep: it cuts 884 trades
  and $5,134 of losses vs jaw-only.
- **Jaw-only (no mouth condition):** combined -$16,565 on
  2,138 trades, win rate 20.5% -- the trend gate matters,
  but even with it the strategy loses.
- **Shipped decision:** keep touch tolerance = 0.5xATR and
  require_mouth = True as the registry config regardless.
  Both were fixed from the source before any backtest was
  run; the sweeps are diagnostic only. No swept variant is
  profitable, so there is nothing to tune toward -- the
  edge is absent, not mis-parameterized. Do not ship a
  wider tolerance or drop the mouth gate on the strength
  of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. SMMA/ATR are
  causal recursions; the touch test and the 5-bar rolling
  window read only bars through the current one; entries
  fire on the first bar of a turn-condition run. The
  truncation test (`test_no_lookahead_truncation`)
  confirms indicator and signal values at bar j are
  identical whether computed on the full frame or on the
  frame truncated at j.
- **Source check:** the Balance Line construction (Jaw =
  SMMA(13) of median price; trade the pullback to the
  balance with the trend resuming) matches the cited
  Bill Williams reference. Three documented choices: the
  Alligator lines are UNSHIFTED (the book's 8/5/3-bar
  forward displacement is a plotting convention, and
  using it causally would be lookahead); the touch band
  is 0.5xATR and the touch window 5 bars (the book does
  not fix either); the both-triggers-same-bar
  enter-neither guard (intrabar order is unknowable from
  OHLC data).
- **Tests:** 17/17 pass (`python3 -m unittest
  strategies.balance_line_pullback.test_balance_line_pullback`).
- **No parameter was tuned to PnL.** Tolerance stays
  0.5xATR, the mouth gate stays required.
