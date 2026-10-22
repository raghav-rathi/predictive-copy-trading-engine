# Original Turtle Rules — Calibration

Entry-channel sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing,
2N stop, 500-bar max hold). The sweep runs **System-1-only variants**
(no S2 failsafe) with (entry channel, exit channel) in
{(20,10), (40,20), (55,20)}; the S1 skip rule stays on in all three,
since it is part of System 1's original spec.

| Entry/Exit | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 20/10 | BTC | 9 | 11.1% | -$407 | -1.29 | 0.14 | -$45.27 |
| 20/10 | ETH | 7 | 28.6% | -$162 | -0.54 | 0.66 | -$23.14 |
| 20/10 | HYPE | 3 | 66.7% | +$15 | +0.11 | 1.17 | +$5.08 |
| 40/20 | BTC | 7 | 28.6% | -$219 | -0.47 | 0.53 | -$31.26 |
| 40/20 | ETH | 6 | 33.3% | -$212 | -0.63 | 0.50 | -$35.25 |
| 40/20 | HYPE | 9 | 22.2% | -$111 | -0.17 | 0.80 | -$12.29 |
| 55/20 | BTC | 7 | 28.6% | -$355 | -0.80 | 0.22 | -$50.78 |
| 55/20 | ETH | 6 | 33.3% | -$212 | -0.63 | 0.50 | -$35.25 |
| 55/20 | HYPE | 13 | 15.4% | -$467 | -0.87 | 0.49 | -$35.91 |

Combined: (20,10) -$554 / 19 trades / PF 0.47; (40,20) -$541 / 22 /
PF 0.62; (55,20) -$1,034 / 26 / PF 0.42.

## One-line verdict

- **Every S1-only variant loses on every coin except one**
  (HYPE +$15 on 3 trades at 20/10 — noise). The skip rule without the
  S2 failsafe starves the system: after the first winning S1 trade in
  each direction, all later S1 signals are skipped and nothing
  replaces them, so each variant takes only 19–26 trades in 7 months
  and bleeds on the 2N stop (profit factors 0.14–0.80).
- Slower channels (40/20, 55/20) do not fix it — fewer, worse trades.
- **Shipped decision:** keep the full S1+S2 original rules exactly as
  specified, fixed **a priori** — adopted before any backtest was run,
  not selected from this sweep. The sweep is diagnostic only: it
  confirms the S2 failsafe is load-bearing (the shipped S1+S2 config
  takes 254 trades vs 19–26 here), and it does not change the shipped
  config. Note the shipped combined (+$332, PF 1.02) is itself
  breakeven noise — see BACKTEST.md — so nothing here argues for
  tuning; it argues the 1h adaptation of these rules has no edge.
