# MESA Sine Wave — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=120 bars.

## Results (shipped config: Ehlers Hilbert sine wave, I2/Q2
smoothing 0.2, long on sine crossing above lead sine, short on
crossing below, exit on the opposite cross, 2xATR stop, 3xATR
trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 972 | 39.8% | -$7,415 | -74.2% | -5.95 | -76.0% | -$7.63 | 0.67 |
| ETH | 950 | 43.3% | -$4,875 | -49.0% | -2.73 | -55.6% | -$5.13 | 0.79 |
| HYPE | 912 | 45.8% | -$2,883 | -28.8% | -1.44 | -35.5% | -$3.16 | 0.89 |
| **Combined** | **2,834** | **42.9%** | **-$15,174** | — | **-4.14** | **-52.3%** | **-$5.35** | **0.79** |

Fees: BTC $6,745, ETH $5,773, HYPE $3,742 (total $16,261).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL. Combined start $30,000,
end $14,806. Exits: BTC 679 signal / 293 stop; ETH 675 / 275;
HYPE 667 / 245.

## Verdict: the worst loser of this batch — a cycle-cross chop machine

Combined -$15,174 on 2,834 trades, and the mechanism is the
problem, not the market: the sine/lead-sine cross fires on
every wiggle of the estimated cycle phase, and on 1h crypto
the estimated phase whipsaws constantly. BTC alone trades
972 times and loses 74.2% of its account (Sharpe -5.95,
MaxDD -76.0%); ETH -49.0%, HYPE -28.8%. Win rate 39.8–45.8%,
profit factor 0.67–0.89 on every coin, and $16,261 of the
loss is fees alone — more than the combined net loss of the
other two strategies in this batch. There is no coin, no
sub-period, no reading in which the shipped config works on
this window: the MESA cycle estimate is a noise amplifier at
this timeframe, and the cross is the trade.

## Calibration note

Shipped the specified I2/Q2 smoothing 0.2. A 0.1/0.2/0.4
smoothing sweep on this batch-46 window is in CALIBRATION.md:
0.1 gives -$15,183 combined (2,623 trades), 0.4 gives
-$16,837 (3,143 trades). The knob barely matters — all three
values lose ~$15–17k — which only confirms the verdict: the
failure is the cross itself, not its smoothing. No in-sample
adoption; the shipped config stays 0.2.

## Mechanism

hl2 = (h + l) / 2; smooth = (4*hl2 + 3*hl2[1] + 2*hl2[2] +
hl2[3]) / 10. Detrender = (0.0962*smooth + 0.5769*smooth[2] -
0.5769*smooth[4] - 0.0962*smooth[6]) * (0.075*Period[1] +
0.54). I1 = detrender[3]; Q1 = the same Hilbert filter on
detrender; jI/jQ = the same filter on I1/Q1; I2 = I1 - jQ,
Q2 = Q1 + jI, each smoothed 0.2/0.8. Phase = atan2(Q2, I2);
dominant cycle from the homodyne discriminator (Re =
I2*I2[1] + Q2*Q2[1], Im = I2*Q2[1] - Q2*I2[1], period =
2*pi/atan2(Im, Re), rate-limited to [0.67x, 1.5x] of the
previous period, clamped 6..50, smoothed 0.2/0.8). Sine =
sin(phase), lead sine = sin(phase + pi/4). Long = sine
crosses above lead sine; short = sine crosses below; exit on
the opposite cross. The harness 2xATR hard stop / 3xATR
chandelier trail sit behind the cross as a safety net for
gap-through moves; 60-bar max hold.

Source: John Ehlers, "Cycle Analytics for Traders" /
"Rocket Science for Traders" ch. 12 —
https://arrowalgo.com/mesa-sine-wave-complete-guide-algorithmic-trading/
(verified URL, given in the batch-46 brief; the guide
confirms the 4-bar WMA smoother, the 0.0962/0.5769 Hilbert
coefficients, I1 = detrender lagged 3, the homodyne
discriminator with period clamped 6..50, and sine/lead-sine
at 45 degrees).

## Limitations

- Single ~8.4-month crypto window; 2,834 trades — the failure
  is overwhelming and consistent, not a sample-size artefact.
- The sine/lead-sine cross fires ~950 times per coin: the
  phase estimate on 1h crypto is noise, and every cross is a
  round-trip fee.
- The calibration sweep shows the smoothing knob cannot
  rescue it (0.1/0.2/0.4 all lose $15k+), so the "right"
  smoothing is not identifiable from this window — and would
  not matter if it were.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped smoothing on this window.
