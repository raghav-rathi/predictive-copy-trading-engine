# StatOasis Rule 5 — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC
(BTC/ETH 6,040 bars, HYPE 6,038 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=120 bars.

## Results (shipped config: RSI(14) > 70 AND Williams %R(14) >
−10 AND SMA(100) falling → short; mirror long; fixed 5-bar hold;
2xATR stop, no trail/target, 5-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 17 | 70.6% | +$781 | +7.8% | +2.27 | -1.5% | +$45.94 | 3.43 |
| ETH | 19 | 47.4% | -$251 | -2.5% | -0.68 | -5.9% | -$13.22 | 0.68 |
| HYPE | 8 | 37.5% | -$215 | -2.1% | -1.25 | -3.0% | -$26.86 | 0.41 |
| **Combined** | **44** | **54.5%** | **+$315** | — | — | — | **+$7.16** | — |

Fees: BTC $226, ETH $172, HYPE $44 (total $443). Fees exceed the
combined net profit — gross PnL before fees was ~$757, so the
5-hour fade is a fee-sensitive trade: the edge, if any, is thin
relative to round-trip costs.

## Verdict: a fade test, not a star — same as the source said

The source's own story was in-sample −$720, out-of-sample
+$2,591 at 75% win rate. This window replays that split
*across coins instead of across time*: BTC is the
out-of-sample-looking leg (70.6% win, PF 3.43, Sharpe +2.27)
while ETH and HYPE are the in-sample-looking legs (both
negative, PF 0.68 and 0.41). Combined +$315 on 44 trades is
positive but not significant, and the coin disagreement is the
honest result: the rule fades double-overbought exhaustion on
BTC and loses fading it on ETH/HYPE in the same window.

- The BTC leg (12 wins of 17) echoes the SPY out-of-sample 75%
  win rate — but 17 trades is far too few to claim the fade
  transfers to crypto. One bad week flips it.
- The ETH leg (−$251, max drawdown −5.9%, the worst of the
  three) shows what the fade costs when overbought keeps running:
  a 5-bar hold against a trending move, exited into strength.
- HYPE fired only 8 times — the triple condition is genuinely
  selective there, and 8 trades proves nothing either way.

Stated plainly: Rule 5 does not validate or fail on this window.
It is a coin-dependent fade with a fee problem (fees $443 vs net
+$315) and a 44-trade sample. A real verdict would need a longer
window and, ideally, a true out-of-sample split — not threshold
tuning on this window (see CALIBRATION.md).

## Mechanism

SHORT on RSI(14) > 70 AND Williams %R(14) > −10 AND SMA(100)
falling; LONG mirror (RSI < 30, %R < −90, SMA(100) rising,
builder-added); fixed 5-bar hold via a bar-count state machine;
2xATR stop, no trail/target, 5-bar max hold. All params fixed a
priori; no optimization.

Source: StatOasis, "Can AI Build a Profitable Trading Strategy?
5 Rules Tested"
(https://statoasis.com/overfit/research/ai-strategy-validation).

## Limitations

- 44 trades total, per-coin samples 8–19: no per-coin statistic
  here is significant; do not quote the BTC leg as an edge or
  the ETH/HYPE legs as a refutation.
- The 5-bar hold is 5 hours here, not 5 days as in the original
  daily SPY test; the momentum conditions fire far more often on
  1h bars.
- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window — least of all
  the RSI / %R thresholds, which are exactly the knobs that
  overfit a fade rule.
