# Fibonacci Pullback Entry — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 00:00 UTC → 2026-10-19 13:00 UTC (5,247 bars BTC/ETH; 5,245 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=260 bars (200-bar SMA + 60-bar swing window).

## Results (shipped config: SMA200 trend filter, trailing 60-bar swing
high/low, long on low dipping to/below the 50% retracement while holding
above 78.6% and closing back above 61.8%; short mirror on the 38.2-50%
bounce zone; exits at the prior swing high/low; 2xATR stop, 100-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 90 | 22.2% | -$482 | -4.8% | -0.15 | -25.6% | -$5.36 | 0.94 |
| ETH | 98 | 18.4% | +$1,375 | +13.8% | +0.79 | -22.1% | +$14.03 | 1.14 |
| HYPE | 86 | 23.3% | +$1,830 | +18.0% | +1.13 | -16.8% | +$21.28 | 1.22 |
| **Combined** | **274** | **21.2%** | **+$2,723** | — | — | — | +$9.94 | — |

## Verdict: mixed (leaning winner)

Classic pullback profile: low-20s win rate, winners larger than losers
(profit factor 1.14-1.22 on ETH/HYPE). ETH (+$1,375, Sharpe +0.79) and
HYPE (+$1,830, Sharpe +1.13) both print positive with contained drawdowns
(-22.1% / -16.8%); BTC is essentially flat (-$482, -4.8%, inside noise).
Combined +$2,723 on 274 trades with $2,409 total fees -- the edge is
real but thin, and the coin split (works on ETH/HYPE, flat on BTC) says
"regime-dependent" rather than "robust". Honest read: a mild winner on
this window, not a system to size up without out-of-sample evidence.

## Calibration note

Swing-window sweep 40/60/90 in CALIBRATION.md: the 40-bar window beats
the shipped 60-bar window on all three coins in-sample. The shipped
60-bar window is kept as specified -- adopting the 40-bar window would
be selecting on the same 7-month window.

## Mechanism

swingH/swingL = trailing 60-bar highest high / lowest low. Long pocket
(uptrend, close > SMA200): lretr50/618/786 = swingH minus 50/61.8/78.6%
of the swing range; entry when the bar's low dips to/below lretr50,
holds above lretr786, and the bar closes back above lretr618. Short
pocket (downtrend): sretr382/50/618 = swingL plus 38.2/50/61.8% of the
range; entry when the bar's high pushes into [sretr382, sretr50], holds
below sretr618, closes back below sretr382. Longs exit at the prior
swing high (target reached), shorts at the prior swing low; the 78.6%
invalidation is approximated by the 2xATR hard stop (the harness cannot
place level stops). 100-bar max hold.

Source: FinancialTechWiz, Fibonacci Retracement (TradingView) —
https://www.financialtechwiz.com/post/fibonacci-retracement-tradingview/

## Limitations

- Single 7-month crypto window; no bull-market or multi-year sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- The 78.6% level stop is approximated by a 2xATR hard stop, which is
  wider/tighter than the true level depending on volatility -- the real
  invalidation would cut some winners and save some losers differently.
- The swing window includes the entry bar itself, so the exit level
  (swingH/swingL) can coincide with the entry bar's extreme.
- 260-bar warmup discards the first ~11 days of data.
