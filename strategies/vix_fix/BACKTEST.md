# VIX Fix Fear-Spike Mean Reversion — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,271 bars BTC/ETH, 5,269 HYPE
(HYPE history starts 2026-03-15 00:00 UTC; BTC/ETH cache opens
2026-03-14 22:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: WVF(22), Bollinger(20, 2.0) on WVF, long on
cross above upper band, exit on cross below midline, mirrored inverse
iWVF short leg, 2xATR stop, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 279 | 52.0% | -$2,429 | -24.3% | -1.98 | -27.7% | -$8.71 | 0.79 |
| ETH | 267 | 52.8% | -$779 | -7.8% | -0.42 | -18.2% | -$2.92 | 0.93 |
| HYPE | 256 | 48.0% | -$2,969 | -29.7% | -2.96 | -34.9% | -$11.60 | 0.70 |
| **Combined** | **802** | **51.0%** | **-$6,178** | — | — | — | -$7.70 | 0.81 |

## Verdict: loser — the fear spike is not a buyable bottom on 1h crypto

Win rates look respectable (48–53%) but profit factors sit at 0.70–0.93:
the midline exit books small relief bounces while the 2xATR stop takes
full breakdowns — average losers are bigger than average winners, and
the math doesn't work. The short inverse leg adds nothing (HYPE, where
greed spikes are most frequent, is the worst leg at PF 0.70).
802 trades across the three coins is not a thin sample; this is a
genuine failure of the setup on this window, not noise. Fees ($6,058
combined) roughly match the gross loss — the edge is absent, not just
eaten. Drawdowns are real: -27.7% BTC, -34.9% HYPE.

## Calibration note

Shipped the specified WVF(22). A 14/22/30 lookback sweep is in
CALIBRATION.md: all three settings lose on all three coins (14 is
least negative at -$4,154 combined, 30 worst at -$7,870). Keeping 22 —
adopting the in-sample best would be cherry-picking a still-losing
setting.

## Mechanism

WVF = 100 × (Highest(High,22) − Low) / Highest(High,22) is Larry
Williams' price-derived fear gauge; a Bollinger Band (20, 2.0) on it
defines "extreme". Long on a cross above the upper band (fear spike),
exit on a cross back below the midline (spike deflated). The short leg
mirrors with iWVF = 100 × (High − Lowest(Low,22)) / Lowest(Low,22):
short on iWVF crossing above its upper band (greed extreme), exit on a
cross below its midline. 2xATR hard stop, 24-bar max hold, no trail,
no target.

Source: Larry Williams VIX Fix (pineify.app writeup) —
https://pineify.app/resources/blog/cm-williams-vix-fix-finds-market-bottoms-indicator-tradingview-pine-script

## Limitations

- Single 7-month crypto window; crypto fear spikes resolve differently
  than the equity bottoms the indicator was designed for.
- The inverse iWVF short leg is the less-reliable published variant —
  greed spikes on crypto can mark the *start* of a leg, not the top.
- Fear spikes cluster in drawdowns, so entries are anti-diversified:
  multiple positions can print into the same waterfall.
- Funding unmodeled; next-bar-open execution vs idealized entry.
