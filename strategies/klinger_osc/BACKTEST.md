# Klinger Volume Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:50 UTC
(ms `[1773446400000, 1792590633848)`): 5,296 bars BTC/ETH, 5,294 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: kvo = EMA(VF,34)−EMA(VF,55), signal =
EMA(kvo,13); long on cross-up, short on cross-down, exits on the
opposite cross, 2xATR stop, 3xATR trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 761 | 47.3% | -$6,170 | -61.7% | -5.60 | -62.4% | -$8.11 | 0.63 |
| ETH | 681 | 46.8% | -$4,905 | -49.1% | -3.67 | -53.5% | -$7.20 | 0.72 |
| HYPE | 680 | 52.8% | -$2,692 | -26.9% | -1.92 | -31.5% | -$3.96 | 0.86 |
| **Combined** | **2,122** | **48.9%** | **-$13,767** | — | — | — | -$6.49 | — |

## Verdict: loser on every coin — a clean reject

No ambiguity here: combined -$13,767 over 2,122 trades, profit factor
below 1.0 on all three coins (0.63 / 0.72 / 0.86), negative Sharpe on
all three (-5.60 / -3.67 / -1.92). BTC is catastrophic (-$6,170,
-62.4% MaxDD, Sharpe -5.60): the kvo/signal cross whipsaws relentlessly
on 1h bars, and with 761 trades the fee bleed is a large share of the
loss — but the profit factor is below 1.0 on gross terms too, so this
is negative edge, not just fee drag. ETH is a slower version of
the same story (-$4,905, -53.5% MaxDD). HYPE loses the least (-$2,692,
PF 0.86, the only win rate above 50%) but is still red.

The mechanism is structurally wrong for this data: Klinger's
cumulative-range term `cm` grows unboundedly within a trend regime, so
`2*dm/cm − 1` decays toward -1 and the volume force saturates — by the
time kvo finally crosses its signal line, the move is already over, and
the cross then fires repeatedly during the chop that follows. A
volume-force breakout oscillator on hourly bars is a fade generator,
not a trend system. 2,122 trades is a thick sample, not a thin one —
this reject is well-evidenced.

## Calibration note

Shipped the specified signal=13. A 9/13/21 signal-line sweep is in
CALIBRATION.md: every setting loses on every coin (best combined
is 13 at -$13,767; 9 is worst at -$16,367; 21 lands at -$13,251).
Signal-line smoothing does not rescue the strategy — the loss is in
the volume-force construction, not the parameter. The 13 was fixed
before any backtest was run and stays.

## Mechanism

Stephen Klinger's volume oscillator: typical price tp=(h+l+c)/3, trend
= sign of tp change, bar range dm=h−l, cumulative range cm kept per
trend regime (cm resets to dm[i−1]+dm[i] on a trend flip), volume force
VF = v*(2*dm/cm−1)*trend*100. kvo = EMA(VF,34) − EMA(VF,55), signal =
EMA(kvo,13). Long on kvo crossing above the signal line, short on the
cross down, exits on the opposite cross. 2xATR hard stop, 3xATR
chandelier trail, 150-bar max hold.

Source: Klinger Volume Oscillator (Stephen Klinger) —
https://www.lumleytrading.com/klinger-oscillator

## Limitations

- The 150-bar max hold + opposite-cross exit lets dead volume-force
  positions bleed: BTC's -62.4% drawdown came from holds that never
  saw the opposite cross in time.
- 2,122 trades means fees are a large share of the gross loss, but
  PF < 1 on every coin even before dissecting fees — this is negative
  edge, not just fee drag.
- Volume semantics differ between Hyperliquid perpetual futures
  (reported contract volume) and the equities volume the indicator
  was designed for — the saturation behavior may be venue-specific.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- The reject stands at every swept signal setting (see CALIBRATION.md).
