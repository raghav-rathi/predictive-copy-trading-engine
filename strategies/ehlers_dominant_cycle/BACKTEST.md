# Ehlers Dominant Cycle — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=60 bars.

## Results (shipped config: band-pass resonator period 20,
bandwidth 0.7 on high-pass detrended close; long on BP cross
above zero, short on BP cross below zero, exit on opposite
cross; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 655 | 31.1% | -$6,750 | -67.6% | -4.73 | -69.4% | -$10.30 | 0.63 |
| ETH | 647 | 32.0% | -$3,897 | -39.1% | -1.93 | -57.2% | -$6.02 | 0.82 |
| HYPE | 637 | 36.9% | -$1,137 | -11.1% | -0.37 | -31.1% | -$1.78 | 0.95 |
| **Combined** | **1,939** | **33.3%** | **-$11,784** | — | **-2.75** | **-47.0%** | **-$6.08** | **0.82** |

Fees: BTC $4,304, ETH $4,455, HYPE $3,072 (total $11,830).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: a loser on every coin — zero-crossing a cycle filter is not a trade

Combined -$11,784 on 1,939 trades (PF 0.82, Sharpe -2.75,
MaxDD -47.0%) loses on all three coins, BTC worst (-$6,750,
Sharpe -4.73, MaxDD -69.4%). HYPE is the least-bad (-$1,137,
PF 0.95, Sharpe -0.37) — close to breakeven, but still
negative. Win rates 31–37% with PF 0.63–0.95 say the
zero-cross entries have no edge: the band-pass output
whipsaws across zero in choppy 1h crypto, and each cross
flips the position at the worst moment — the resonator lags
the cycle it measures, so the cross fires after the move it
was meant to catch. Signal exits (380 / 373 / 423) and stop
exits (275 / 274 / 214) are roughly balanced, so neither the
cross exit nor the harness stop is saving the trade. Honest
read: the dominant-cycle measurement itself is sound (the
sine-wave tests recover periods 20 and 40 correctly), but
trading its zero crossings on 1h bars loses money on every
coin in this window.

## Mechanism

High-pass detrender (Ehlers one-pole, cutoff 61.5 bars — one
octave below the 30.8-bar lower pass-band edge) removes the
trend from the close; the two-pole resonator (beta =
cos(2π/20), gamma = 1/cos(4π·0.7/20), alpha = gamma −
sqrt(gamma²−1); BP_t = 0.5(1−alpha)(x_t − x_{t−2}) +
beta(1+alpha)BP_{t−1} − alpha·BP_{t−2}) isolates the cycle
near period 20. Long on BP crossing above zero, short on BP
crossing below zero, exit on the opposite cross. The dominant
cycle period (2× bars between successive BP zero crossings,
assigned at the completing crossing, forward-filled, SMA-10,
clamped [6, 50]) is a diagnostic column only. The harness
2xATR stop / 3xATR trail / 120-bar max hold sit behind the
cross exit.

Source: John F. Ehlers — "Cycle Analytics for Traders" (2013),
band-pass filter chapter —
https://docs.wickra.org/Indicators/Indicator-BandpassFilter
(resonator coefficients and filter structure per the task
brief; the high-pass cutoff derivation — lower edge 20 /
(1 − 0.7/2) = 30.8, one octave below = 61.5 — is documented
in indicators.py).

## Limitations

- Single ~8.4-month crypto window; the verdict is negative on
  all three coins, so no coin-dependence caveat rescues it.
- The zero-cross signal inherits the resonator's lag: the
  cross is confirmed after the cycle has already turned.
- The dominant-cycle diagnostic is not traded; a system that
  sized or timed entries by the measured cycle would be a
  different strategy.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped bandwidth on this window.
