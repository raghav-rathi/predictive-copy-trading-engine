# Fisher Transform Reversal — backtest report

## Setup
- Data: cached Hyperliquid 1h candles, BTC / ETH / HYPE, 365d lookback (cache
  coverage: 5008 / 5008 / 5006 bars, ~209 days, through Oct 2026).
- Costs: 0.045% taker + 0.01% slippage per side. Sizing: 1% risk per trade,
  2xATR hard stop, no trailing, no target, max 3x leverage, $10k equity.
- Warmup: 80 bars. Funding: excluded (use_funding=False).
- Runs: `python3 scripts/run_strategy_backtest.py fisher_transform BTC ETH HYPE`
  plus a throwaway calibration script comparing both variants
  (see Calibration below).

## Calibration: plain vs ADX(14)>20-gated entries
Combined-net-PnL winner decides the shipped variant.

| Coin | plain trades | plain net $ | gated trades | gated net $ |
|------|-------------:|------------:|-------------:|------------:|
| BTC  | 1466 |  -8,821.01 | 1041 |  -7,799.44 |
| ETH  | 1445 |  -7,287.89 |  958 |  -4,160.29 |
| HYPE | 1570 |  -8,401.69 | 1084 |  -7,743.41 |
| **combined** | **4481** | **-24,510.59** | **3083** | **-19,703.14** |

Shipped: **gated** — it lost less on every coin (combined −$19.7k vs −$24.5k
plain). The ADX gate cuts ~31% of trades and the worst whipsaws, but does not
rescue the strategy.

## Shipped variant (gated) results

| Coin | trades | win% | net $ | net % | Sharpe | maxDD % | expectancy $ | profit factor |
|------|-------:|-----:|------:|------:|-------:|--------:|-------------:|--------------:|
| BTC  | 1041 | 28.0 | -7,799.44 | -77.99 | -8.77 | -78.02 | -7.49 | 0.56 |
| ETH  |  958 | 30.2 | -4,160.29 | -41.45 | -2.81 | -46.26 | -4.34 | 0.79 |
| HYPE | 1084 | 29.0 | -7,743.41 | -77.38 | -9.47 | -77.72 | -7.14 | 0.54 |
| **combined** | **3083** | — | **-19,703.14** | — | — | — | — | — |

Fees alone: BTC $5,864.92, ETH $5,871.00, HYPE $2,686.34 (funding excluded).

## VERDICT: LOSER
The Fisher Transform reversal loses badly on all three coins at every
parameterization tested. Win rate sits at 28–30%, profit factor 0.54–0.79,
and the equity curve bleeds −42% to −78% with max drawdowns matching the
full loss. The ADX(14)>20 gate helps (it filters the choppiest entries) but
the core problem is structural: fisher vs its 1-bar lag crosses flip every
~3–4 bars on 1h, so the system trades constant whipsaws where each round
trip pays 0.11% in costs against ~28% wins. This variant should not ship to
paper trading without a fundamental redesign (longer trigger, cooldowns, or a
different exit engine).

## Calibration note
Calibration ran plain (raw fisher/trigger crosses) against an ADX(14)>20
entry gate on the same 1h cached candles for BTC, ETH, and HYPE. The gate
shipped because it improved combined net PnL by ~$4,800 — fewer trades
(3083 vs 4481), higher win rate on ETH (30.2% vs 28.5%), and a better
profit factor on ETH (0.79 vs 0.69) — while winning on each coin
individually, so the choice does not depend on one outlier. But the
improvement is "loses less," not "wins": the gated variant still nets
−$19.7k combined, so calibration picked the less-bad loser honestly.

## Mechanism summary
Normalized 10-bar price position raw=(c−lo₁₀)/(hi₁₀−lo₁₀), recursively
smoothed value=0.66·(2·raw−1)+0.34·value_prev (exactly an EMA, alpha=0.66),
clipped to ±0.999, Fisher-transformed fr=0.5·ln((1+value)/(1−value)),
polished with a 0.5-EMA; trigger = fisher shifted one bar. Long when fisher
crosses above trigger (and ADX14>20 in the gated variant), short on cross
below; exit on cross-back or extreme levels (fisher>+2.5/−2.5). 2xATR stop.

## Source
- John Ehlers, Fisher Transform (Technical Analysis of Stocks & Commodities) —
  https://fxprosystems.com/ehlers-fisher-transform/

## Limitations
- Single 365d-lookback (cache-limited) window; no walk-forward or
  out-of-sample validation performed.
- Hyperliquid spot/perp fee tier only; live funding costs excluded.
- No shorting constraints modeled (borrowing, borrow-rate) beyond costs.
- HYPE's shorter history and lower liquidity make its row the noisiest.
- Whipsaw risk is extreme by construction: entry triggers on a 1-bar lag
  cross, so consecutive opposite signals can occur within 2 bars.
