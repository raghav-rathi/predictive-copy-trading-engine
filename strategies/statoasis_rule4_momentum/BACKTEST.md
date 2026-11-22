# StatOasis Rule 4 — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned window
2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC: BTC/ETH 6,040 bars,
HYPE 6,038 bars.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=150 bars.

## Results (shipped config: RSI > 55 AND %K > 50 AND %R > −50
AND 120h return > 1%, fixed 10-bar time exit, 2xATR stop, no
trail, 10-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 327 | 40.1% | -$2,351 | -23.5% | -1.38 | -35.3% | -$7.19 | 0.82 |
| ETH | 330 | 37.0% | -$1,513 | -15.1% | -0.66 | -29.7% | -$4.59 | 0.89 |
| HYPE | 369 | 48.0% | +$1,202 | +12.0% | +0.77 | -18.1% | +$3.26 | 1.08 |
| **Combined** | **1,026** | **41.9%** | **-$2,663** | — | — | — | **-$2.60** | — |

Fees: BTC $2,909, ETH $2,274, HYPE $2,011 (total $7,193).

## Verdict: loser — the rule does not survive the move to 1h crypto

1,026 trades is a large sample, and it loses on two of three
coins with deep drawdowns (BTC −35.3%, ETH −29.7%). The
combined −$2,663 is a genuine negative, not noise:

- **The 10-bar hold churns.** The rule re-enters constantly
  (conditions stay true for days in a trend), so the book is
  nearly always in the market, paying $7,193 in fees — 2.7x
  the net loss. The source's frictionless SPY test never paid
  that bill; on 1h crypto with real costs, a 10-hour hold with
  no exit discipline is a fee machine.
- **The win rate collapsed vs the source.** SPY daily OOS was
  69.2%; here it is 37–48%. Momentum confirmation on daily
  bars is a different animal from momentum confirmation on
  hourly bars — by the time all four oscillators agree on 1h,
  the move is usually exhausted, and the fixed 10-bar hold
  then rides the reversal.
- **HYPE is the exception, not the refutation.** +$1,202 at
  PF 1.08 on 369 trades is barely above breakeven and is
  dwarfed by the BTC/ETH losses; with three coins tested, one
  mildly positive leg is expected by chance.
- The 2xATR stop fired often enough that the "fixed 10-bar
  hold" was frequently cut short — the stop, not the time
  exit, did much of the trade management, which means the
  tested object drifted from the source rule.

Stated plainly: Rule 4's SPY-daily result does not transfer to
1h crypto. This is the honest-loser outcome the source study
itself anticipates — its Monte Carlo screen was on SPY daily,
and nothing in it promised hourly crypto.

## Mechanism

RSI(14) > 55 AND Stochastic %K(14, smooth 3) > 50 AND Williams
%R(14) > −50 AND 120h return > 1% → long, fixed 10-bar time
exit, no indicator exit; short side is a builder-added mirror.
2xATR stop, no trail, 10-bar max hold. All params fixed a priori
from the source; no optimization.

Source: StatOasis — "Can AI Build a Profitable Trading
Strategy? 5 Rules Tested" (Rule 4)
(https://statoasis.com/overfit/research/ai-strategy-validation).

## Limitations

- Single 8-month crypto window (a falling, choppy regime for
  BTC/ETH); funding unmodeled; next-bar-open execution.
- The source's validation (OOS + Monte Carlo on SPY daily) does
  not cover this adaptation — different asset, different
  timeframe, plus a builder-added short mirror the source never
  tested.
- Never tune the shipped parameters on this window — widening
  the hold, loosening the thresholds, or dropping the short side
  until the sample turns positive would be pure overfitting.
