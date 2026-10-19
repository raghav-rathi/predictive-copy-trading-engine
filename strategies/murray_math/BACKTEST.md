# Murrey Math Octave Reversal — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-19 13:00 UTC
(ms `[1773446400000, 1792414800000)`): 5,247 bars BTC/ETH, 5,245 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=100 bars (64-bar frame + ATR spin-up).

## Results (shipped config: 64-bar frame, bottom/top-zone touch +
reclaim of L1 / loss of L7 for entry, exit at 4/8 pivot or opposite
extreme touch, 2xATR stop, 80-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 172 | 43.0% | -$2,206 | -22.2% | -1.86 | -30.9% | -$12.83 | 0.78 |
| ETH | 165 | 47.9% | -$376 | -3.7% | -0.19 | -15.8% | -$2.28 | 0.96 |
| HYPE | 195 | 43.6% | -$1,747 | -17.3% | -1.43 | -20.4% | -$8.96 | 0.83 |
| **Combined** | **532** | **44.7%** | **-$4,329** | — | — | — | -$8.14 | — |

## Verdict: loser on all three coins

Negative expectancy everywhere, profit factor below 1.0 on every coin,
combined -$4,329 on 532 trades. This is the classic mean-reversion
failure mode in a trending window: Mar–Oct 2026 was a persistent
downtrend on the majors, and fading breakdowns at "0/8" into lower lows
bleeds. Worse, the 64-bar frame re-anchors the grid lower with every
down leg, so "cheap" is always relative to a falling frame — the bounce
never comes and the 2xATR stop takes the loss. ETH is nearly flat
(-$376, PF 0.96); BTC and HYPE are firmly negative. Fees ($3,679
combined) are material but not the story: the gross edge is absent.

## Calibration note

Shipped the specified 64-bar frame. A 32/64/128-bar frame sweep is in
CALIBRATION.md: the 32-bar frame is worse everywhere (whipsaw), the
128-bar frame flips ETH positive (+$1,131) but deepens HYPE's loss
(-$3,209) — coin-dependent, not a robust improvement. Keep 64.

## Mechanism

Trailing 64-bar high/low = the Murrey frame; octave = (high−low)/8;
grid lines L0=[0/8] … L8=[8/8], 4/8 (L4) the pivot. Bottom zone =
0/8–1/8 (bar low ≤ L1 + 0.1·octave), top zone = 7/8–8/8 (bar high ≥
L7 − 0.1·octave). Long when the close crosses back above L1 with a
bottom-zone touch in the last 3 bars; short on the mirror at L7. Long
exits when the close crosses above the 4/8 pivot or the top zone is
touched (short mirrors). 2xATR hard stop, 80-bar max hold.

Source: Murrey Math Lines v6 —
https://th.tradingview.com/script/Lm6H0fRT-Murrey-Math-Lines-v6/

## Limitations

- Single 7-month, trend-dominated crypto window; the strategy is a
  mean-reversion system and this window punishes exactly that.
- The grid re-anchors with the rolling frame — in a sustained trend the
  "extreme" keeps moving against the position.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- 64-bar frame needs ~100 bars of warmup before signals are valid.
