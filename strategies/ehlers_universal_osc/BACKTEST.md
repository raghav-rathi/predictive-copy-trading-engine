# Ehlers Universal Oscillator — Backtest

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
bandwidth 0.3 on median price, AGC-normalized by rolling
100-bar RMS; long on normalized output crossing above the
0.9x trigger, short on crossing below, exit on opposite
cross; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 905 | 31.8% | -$7,941 | -79.4% | -6.50 | -80.8% | -$8.78 | 0.56 |
| ETH | 908 | 33.6% | -$6,863 | -68.5% | -4.47 | -71.7% | -$7.56 | 0.65 |
| HYPE | 905 | 36.0% | -$5,192 | -51.8% | -3.03 | -56.6% | -$5.74 | 0.76 |
| **Combined** | **2,718** | **33.8%** | **-$19,996** | — | **-5.94** | **-68.9%** | **-$7.36** | **0.66** |

Fees: BTC $4,554, ETH $4,123, HYPE $2,969 (total $11,646).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: the worst of the batch — the trigger cross whipsaws ~900 times per coin

Combined -$19,996 on 2,718 trades (PF 0.66, Sharpe -5.94,
MaxDD -68.9%) is a two-thirds drawdown of the $30k combined
start: every coin loses more than half its equity, BTC worst
(-$7,941, Sharpe -6.50, MaxDD -80.8%). Win rates 32–36% with
PF 0.56–0.76 say the trigger-cross entries have no edge at
all on 1h crypto — the normalized oscillator oscillates
around its own lagged trigger constantly, so the cross fires
on noise and each flip pays the spread and fees. Signal exits
(617 / 615 / 674) outnumber stop exits (288 / 293 / 231)
~2:1, so positions are churned by the next counter-cross
before the trend can pay. The AGC normalization works as
designed (the sine test recovers unit RMS), and the resonator
is correct — the signal itself is just not a trade on this
time frame. Honest read: do not trade this; of the three
batch-47 strategies it loses the most money the fastest.

## Mechanism

Median price ((h+l)/2) through the two-pole resonator (beta
= cos(2π/20), gamma = 1/cos(4π·0.3/20), alpha = gamma −
sqrt(gamma²−1); BP_t = 0.5(1−alpha)(med_t − med_{t−2}) +
beta(1+alpha)BP_{t−1} − alpha·BP_{t−2}), AGC-normalized by
its rolling 100-bar RMS (0 when the RMS is 0), trigger line
= 0.9 × the prior bar's normalized output. Long on the
normalized output crossing above the trigger, short on it
crossing below, exit on the opposite cross. The harness
2xATR stop / 3xATR trail / 120-bar max hold sit behind the
cross exit.

Source: John F. Ehlers — "Cycle Analytics for Traders" (2013),
band-pass filter chapter —
https://www.tradingview.com/script/jtvNFAgS-Ehlers-Band-Pass-Filter/
(resonator coefficients, AGC normalization, and the 0.9x
delayed trigger per the task brief).

## Limitations

- Single ~8.4-month crypto window; the verdict is negative on
  all three coins, so no coin-dependence caveat rescues it.
- The trigger is a lagged copy of the signal itself, so the
  cross is a momentum flip on a smoothed oscillator — it
  fires on every wiggle in choppy markets (~900 trades/coin).
- The AGC window (100 bars) is slow relative to the 20-bar
  resonator, so the normalization scale lags regime changes.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped trigger scale on this window.
