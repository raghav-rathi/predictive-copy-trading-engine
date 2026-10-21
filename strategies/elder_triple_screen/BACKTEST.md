# Elder Triple Screen — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:00 UTC
(ms `[1773446400000, 1792590584428)`): 5,296 bars BTC/ETH, 5,294 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2.5xATR stop, 3x leverage cap,
$10k start. WARMUP=200 bars.

## Results (shipped config: 6h MACD(12,26,9) histogram trend screen,
1h Force Index EMA(2) wave, long on trend-up + FI cross below 0, short on
trend-down + FI cross above 0, exit when the trend screen flips, 2.5xATR
stop, 3.5xATR trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 186 | 24.2% | -$3,281 | -32.8% | -3.56 | -33.5% | -$17.64 | 0.52 |
| ETH | 182 | 31.9% | -$1,662 | -16.6% | -1.43 | -19.0% | -$9.13 | 0.73 |
| HYPE | 180 | 35.0% | -$1,759 | -17.6% | -1.84 | -20.6% | -$9.77 | 0.73 |
| **Combined** | **548** | **30.3%** | **-$6,702** | — | — | — | -$12.23 | — |

## Verdict: loser on all three coins — the worst of this batch

Red everywhere, and not marginally: combined -$6,702 on 548 trades,
profit factor below 0.75 on every coin, win rates 24–35%. BTC is the
bleeder (-$3,281, Sharpe -3.56, MaxDD **-33.5%** — a third of the
account gone on one leg). ETH and HYPE lose less only because they
trade smaller ranges; both still print PF 0.73 with expectancy near
-$10/trade.

The mechanism is the problem, not the parameters (see
CALIBRATION.md): the 6h MACD-histogram trend screen is too slow for 1h
crypto. By the time the histogram confirms "trend up", the move is
mature; the Force Index pullback entry then buys the dip into a
tide that is already rolling over, and the slow screen flip lets the
loser run before the exit prints. In a 7-month window dominated by
distribution and breakdowns, buying every oversold 1h wave against a
lagging higher-timeframe trend is systematically the wrong side.

A machinery check on a synthetic steady uptrend (83 long entries,
89.7% win rate, +$11.4k) confirms the code does what the spec says —
the signal is genuinely anti-predictive here, not misimplemented.

## Calibration note

Shipped the specified MACD(12,26,9) on the 6h screen. A
(12,26,9)/(8,17,9)/(16,32,9) sweep is in CALIBRATION.md: **every cell
of the sweep loses on every coin** (PF 0.49–0.82, net -$1,177 to
-$3,412). (12,26,9) is the shipped config a priori; nothing in the
sweep would justify adopting a different setting anyway.

## Mechanism

Screen 1 (the tide): 1h bars resampled to 6h (o=first, h=max, l=min,
c=last, v=sum); MACD(12,26,9) on 6h closes; trend_up = histogram > 0
and rising, trend_down = histogram < 0 and falling. Each 1h bar reads
the last 6h bar that fully closed at or before its open (no
lookahead). Screen 2 (the wave): 1h Force Index = (c - c[1]) * v,
smoothed to EMA(2). Long when the tide is up and the wave crosses back
below zero (pullback); short when the tide is down and the wave crosses
back above zero. Exit when the trend screen flips (Elder's exit rule).
Screen 3's intraday stop-entry precision is approximated by the
harness's next-bar-open execution. 2.5xATR hard stop, 3.5xATR
chandelier trail, 150-bar max hold.

Source: Triple Screen (Alexander Elder, Trading for a Living) —
https://tradingwriters.substack.com/p/elders-triple-screen-trading-system

## Limitations

- Single 7-month crypto window; 548 trades is a decent sample for a
  negative verdict, but still one regime.
- BTC MaxDD -33.5%: the slow trend-screen exit lets counter-tide
  positions bleed far.
- The factor-5 resample (1h→6h) inherits Elder's daily→weekly ratio,
  but 6h MACD(12,26,9) spans ~6.5 days of 1h data — arguably the wrong
  clock for crypto's 24/7 volatility.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Do not ship this config live on the evidence here.
