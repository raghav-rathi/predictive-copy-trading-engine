# Ichimoku + Stochastic — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned batch-45 window: 2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC (BTC 6,111 bars, ETH 6,111 bars, HYPE
6,109 bars — exactly the expected counts).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR(14) stop, 3x
leverage cap, $10k start, long/short. WARMUP=80 bars.

## Results (shipped config: Ichimoku 9/26/52 cloud filter +
Stochastic (14,3,3) cross from <30 / >70, exit on opposite
cross or close back into the cloud, 2xATR(14) stop, 3xATR
chandelier trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 82 | 29.27% | -$1,013.17 | -10.13% | -2.97 | -12.50% | -$12.36 | 0.44 |
| ETH | 67 | 28.36% | -$654.73 | -6.55% | -1.74 | -7.45% | -$9.77 | 0.58 |
| HYPE | 74 | 24.32% | -$803.21 | -8.03% | -2.34 | -9.35% | -$10.85 | 0.45 |
| **Combined** | **223** | **27.35%** | **-$2,471.10** | — | — | — | **-$11.08** | — |

Fees: BTC $912.65, ETH $531.34, HYPE $347.60 (total $1,791.59).
Gross PnL before fees: -$679.51 combined — the system loses
before costs too, and fees roughly triple the damage.

Exit reasons: BTC 79 signal / 3 stop; ETH 61 signal / 6 stop;
HYPE 71 signal / 3 stop. No max-hold exits. Sides roughly
balanced (BTC 37 long / 45 short; ETH 32 / 35; HYPE 39 / 35).
Median hold: 2 bars on every coin.

## Verdict: loser — no edge on this window

Combined -$2,471.10 across 223 trades with a 27.35% win rate
and a -$11.08 expectancy is a clear loser, and it loses on
all three coins (Sharpe -1.74 to -2.97, profit factor 0.44–
0.58). Do not quote it as anything but a losing system.

- The exit mix is the diagnosis: 211 of 223 exits are signal
  exits with a median hold of 2 bars. The entry fires when
  price is sitting on the cloud edge (that is where a
  Stochastic turn from oversold usually happens), and the
  very next bar's close slips back into the cloud and exits
  the trade. The system pays two sides of fees for a 2-hour
  hold, over and over.
- It is not just a fee story: gross PnL before fees is
  -$679.51. The entries themselves are slightly
  negative-expectancy, and the 0.055%-per-side cost drag turns
  a small gross loss into a -$2,471 net loss.
- The 3xATR chandelier trail almost never matters — with a
  2-bar median hold, positions never live long enough to trail.

Stated plainly: the cloud filter plus oversold Stochastic
cross does not produce a tradable edge on 1h crypto in this
window. The combination of a slow trend filter and a fast
mean-reversion trigger fires entries at the worst point of
the cloud edge, and the cloud re-entry exit cuts them before
any trend leg develops.

## Mechanism

LONG when close > cloud top AND Tenkan > Kijun AND %K
crosses above %D while %K < 30; SHORT on the mirror. Exit on
the opposite Stochastic cross or a close back inside/through
the cloud. 2xATR(14) stop, 3xATR chandelier trail, 120-bar
max hold. All params fixed a priori; no optimization.

Source: Ichimoku Kinko Hyo (Goichi Hosoda) + Stochastic
Oscillator (George Lane)
(https://www.investopedia.com/terms/i/ichimoku-cloud.asp).

## Limitations

- Single 8-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- 223 trades is a reasonable sample, and the loss is
  consistent across all three coins — the verdict is not a
  one-coin artifact.
- Never tune the shipped parameters on this window — least
  of all the %K < 30 / > 70 gates or the cloud re-entry exit,
  which directly control how many trades fire and how fast
  they exit.
