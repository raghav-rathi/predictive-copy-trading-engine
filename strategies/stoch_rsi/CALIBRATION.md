# Stochastic RSI — Calibration

%K/%D smoothing sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same
costs/sizing, 2xATR stop, 3xATR trail, 60-bar max hold). Smoothing
is the strategy's natural knob: (2,2) reacts fastest to the raw
stochastic line (more signals, more whipsaw), (5,5) smooths the most
(fewer signals, more lag). The sweep re-runs
`add_indicators(df, k_n=X, d_n=Y)` only — signals and risk are
unchanged.

| (k,d) | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| (2,2) | BTC | 355 | 29.0% | -$5,106 | -4.11 | 0.58 | -$14.38 |
| (2,2) | ETH | 337 | 37.7% | +$304 | +0.31 | 1.02 | +$0.90 |
| (2,2) | HYPE | 321 | 34.6% | -$1,144 | -0.61 | 0.92 | -$3.56 |
| (3,3) (shipped) | BTC | 312 | 30.1% | -$4,524 | -3.44 | 0.64 | -$14.50 |
| (3,3) (shipped) | ETH | 301 | 38.9% | -$1,286 | -0.67 | 0.90 | -$4.27 |
| (3,3) (shipped) | HYPE | 278 | 37.8% | +$1,305 | +0.86 | 1.10 | +$4.69 |
| (5,5) | BTC | 253 | 30.0% | -$4,193 | -3.35 | 0.62 | -$16.57 |
| (5,5) | ETH | 239 | 36.0% | -$1,530 | -0.92 | 0.87 | -$6.40 |
| (5,5) | HYPE | 224 | 38.4% | -$104 | +0.02 | 0.99 | -$0.46 |

## One-line verdict

- **(2,2):** fastest trigger, most trades (1,013 combined) — best on
  ETH (+$304, the only other green coin-read in the sweep) and
  worst on BTC (-$5,106, the worst single read anywhere) and HYPE
  (-$1,144). More signals, more churn, same disease.
- **(5,5):** fewest trades (716), least lag-tolerant — worst on ETH
  (-$1,530) and dead flat on HYPE (-$104, PF 0.99). Smoothing does
  not fix a signal with no edge; it just trades less.
- **(3,3):** least-bad combined (-$4,505 vs -$5,946 for (2,2) and
  -$5,827 for (5,5)) and the only setting green on HYPE — but that
  is an in-sample observation, not a justification.
- **Shipped decision:** keep the specified (k,d)=(3,3) as the
  registry config regardless. It was fixed before any backtest was
  run; adopting it *because* it is least-bad in-sample would still
  be in-sample selection. The honest read: the smoothing knob moves
  the loss around between coins (per-coin winners split across all
  three settings) without ever producing a profitable book, which
  says the 20/80 exhaustion trigger itself is the problem on 1h
  crypto — not its smoothing.
