# Batch-4 strategy summary (2026-10-13)

12 strategies, 75 build commits + 2 merge commits + infra/docs commits,
105 unit tests green. Backtests: Hyperliquid 1h candles BTC/ETH/HYPE,
2026-03-14 → 2026-10-10/13, $10k equity, 1% risk/trade, 3x leverage cap,
0.045% taker + 0.01% slippage per side, no funding accrual.
Honest verdicts — losers named.

## Batch A (classics: DeMark / Raschke / Wilder)

| slug | source | result |
|---|---|---|
| td_sequential | Tom DeMark Sequential (setup 9 + countdown 13, perfection filter, TDST) | **Earner**: ETH +$4,076 (Sharpe 2.80), BTC +$1,590; HYPE loser. Shipped: 1.5xATR stop + 96-bar hold (sweep-stable on all 3 coins) |
| holy_grail | Raschke "Holy Grail" (ADX>30-rising trend + first 20-EMA touch) | Non-earner: 11 trades in 7 months; BTC/ETH 0% WR. Gate not diluted |
| wilder_dm | Wilder DMS (DI cross + ADX>25-rising, SAR/range exits; SAR loop local) | Research-grade: 8 trades total, conjunction almost never fires on 1h |
| mass_index | Dorsey Mass Index (bulge 27/26.5; SMA(20) direction = OUR extension) | Mixed: ETH +$1,882 (Sharpe 2.06), HYPE +$157, **BTC -$927 — do not run on BTC** |

## Batch B (classics: Vortex / Camarilla / Blau / Raschke)

| slug | source | result |
|---|---|---|
| vortex | Botes & Siepman Vortex Indicator (VI+/VI- cross, ADX>20 gate shipped) | Loser on BTC/ETH at every setting; HYPE +$544 only |
| camarilla_pivots | Nick Stott Camarilla (R3/S3 fade, UTC session; breakout variant tested) | Fade loses on all 3 (59% WR, negative expectancy). Breakout/rolling variant positive but thin — not shipped |
| tsi | Blau True Strength Index (double-smoothed, signal cross, zero-gate) | **HYPE +$4,304 (Sharpe 2.73)** — batch-4 best single result; BTC/ETH losers. Coin-scoped, not general |
| raschke_anti | Raschke "Anti" (3/10/16, %D-slope trend, %K-hook re-alignment) | **Decisive loser everywhere** (BTC -$5,498, Sharpe -5.10). No param rescue |

## Batch C (Elder + fresh 2026 finds)

| slug | source | result |
|---|---|---|
| force_index | Elder Force Index (FI13 trend, FI2 pullback trigger) | Loser everywhere (2,533 trades, fee drag ~$3.4k, PF 0.53–0.89) |
| triple_screen | Elder Triple Screen (4h MACD-hist tide + FI2 wave; composes force_index) | Loser everywhere (PF 0.54–0.66); three-screen conjunction does NOT produce sparse signals (~1,030 trades) |
| rsi_extreme_edge | @Vision33X / visioneth rsi-extreme-edge (RSI(14) 1H: >90 cross-back short, <10 cross-back long; ATR 1.5x stop, 1.5R target) | **Unvalidatable on 1h**: 4 trades in 7 months. Author's coin-personality findings can't be confirmed/denied at this timeframe |
| jhadchiti_trend | jhadchiti crypto-trading-system (55-bar breakout + BTC SMA(200) regime + ±20bp/8h funding filter + coin-vs-BTC momentum) | **Mixed**: ETH +$556 (23.4% WR, 3.75x win/loss skew — author's profile; positive in 7/9 param combos); HYPE -$1,268; BTC 0 trades by construction (benchmark degenerate in momentum filter) |

## Empirical direction

Exhaustion counters (TD Sequential) and double-smoothed momentum (TSI on
HYPE) are the only positive classic systems this batch; pullback-continuation
systems (Holy Grail, Raschke Anti, Force Index) fail decisively on 1h crypto.
HYPE remains the friendliest coin for momentum systems; BTC 1h chop kills
unfiltered oscillators. Per-coin, per-strategy detail lives in each
strategy's BACKTEST.md / CALIBRATION.md.
