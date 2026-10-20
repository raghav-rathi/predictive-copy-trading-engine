# VPIN Toxicity Exhaustion — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,271 bars BTC/ETH (cache starts
2026-03-14 02:00 UTC), 5,269 HYPE (HYPE history starts 2026-03-15
00:00 UTC). Last bar 2026-10-20 12:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=320 bars.

## Results (shipped config: bulk volume classification per bar, bucket
size = trailing 50-bar mean volume, VPIN = mean |buy−sell|/bucket over
50 buckets, percentile trigger > 0.90 with new 20-bar low/high,
2xATR stop, 2xATR target, 48-bar max hold, no signal exits)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 50 | 48.0% | -$833 | -8.3% | -1.35 | -15.8% | -$16.66 | 0.70 |
| ETH | 66 | 45.5% | -$1,619 | -16.2% | -2.45 | -16.7% | -$24.53 | 0.60 |
| HYPE | 62 | 43.5% | -$1,092 | -10.9% | -1.78 | -17.8% | -$17.62 | 0.68 |
| **Combined** | **178** | **45.5%** | **-$3,545** | — | — | — | -$19.91 | 0.65 |

## Verdict: loser — the exhaustion read does not pay on 1h crypto

178 trades, negative on all three coins with profit factors 0.60–0.70
and negative expectancy everywhere (−$17 to −$25/trade). The academic
VPIN measures informed-flow toxicity ahead of *volatility* events, not
direction: fading a panic extreme on 1h crypto bars means stepping in
front of a move that keeps going — the 2xATR target rarely fills before
the 2xATR stop or the 48-bar max hold does the damage. Win rates near
45% with PF < 0.7 say the fade is systematically early/wrong: on these
timeframes "toxic" flow is usually just momentum. Fees ($1,128
combined) are a sideshow, not the story. Honest read: the mechanism
does not translate from the paper's volatility context to a
directional 1h fade.

## Calibration note

Shipped the specified 0.90 percentile trigger. A 0.85/0.90/0.95 sweep
is in CALIBRATION.md: every setting loses on every coin; 0.95 is least
negative in-sample (combined −$2,917 vs −$3,545 shipped) but on only
109 trades — too thin to adopt. Keep 0.90 as specified; the trigger is
not a rescue knob, the fade premise itself fails here.

## Mechanism

Bulk Volume Classification per 1h bar (`buyV = v·(c−l)/(h−l)`, 50/50 on
flat bars) accumulates into volume buckets sized at the trailing 50-bar
mean volume (remainder carried across buckets). VPIN = mean
|buy−sell|/bucket over the last 50 completed buckets, ranked as a
percentile over the trailing 252 bars. Long when percentile > 0.90 AND
the close makes a new 20-bar low (panic exhaustion); short symmetric
on new 20-bar highs. No signal exits — 2xATR stop, 2xATR target,
48-bar max hold manage the trade. Documented as an experimental
exhaustion read of the academic toxicity metric, not a faithful VPIN
implementation (the original is a volatility filter, not a fade
trigger).

Source: VPIN (Easley/de Prado/O'Hara via jheusser.github.io) —
https://jheusser.github.io/2013/10/13/informed-trading.html

## Limitations

- Single 7-month crypto window; 178 trades, all negative.
- The toxicity percentile is a slow 252-bar rank — by the time it
  triggers, the panic is usually mid-extension, not exhausted.
- Bucket size from a 50-bar volume mean makes VPIN noisy on crypto's
  spiky volume; imbalance ≈ momentum proxy on 1h bars.
- Funding unmodeled; next-bar-open execution vs idealized entry.
