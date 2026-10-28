# Smoothed Heikin-Ashi — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), filtered to t >= 1773525600000: BTC/ETH 5,445 bars,
2026-03-14 22:00 UTC → 2026-10-27 13:00 UTC; HYPE 5,443 bars,
2026-03-15 00:00 UTC → 2026-10-27 13:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run, funding off).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=30 bars.

## Results (shipped config: EMA(5)-smoothed HA close/open cross
entry, opposite cross exit, 2xATR stop, 2.5xATR trail, 168-bar
max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 775 | 24.5% | -$7,655.37 | -76.45% | -7.04 | -77.92% | -$9.88 | 0.57 |
| ETH | 745 | 28.1% | -$5,080.30 | -50.58% | -3.20 | -53.45% | -$6.82 | 0.74 |
| HYPE | 715 | 29.2% | -$4,431.56 | -43.83% | -2.78 | -44.72% | -$6.20 | 0.77 |
| **Combined** | **2,235** | — | **-$17,167.23** | — | — | — | **-$7.68** | — |

Fees: BTC $4,820.08, ETH $4,555.21, HYPE $2,609.44 (total
$11,984.73). Signal entries alternate long/short on every cross
(BTC 390 / 390, ETH 374 / 374, HYPE 360 / 360); trade counts run
slightly below entry counts because the final open position per
coin is unclosed at the window end.

## Verdict: loser — the batch's worst

-$17,167.23 on 2,235 trades, with BTC down 76% and a -77.92% max
drawdown. The per-trade expectancy is only -$6 to -$10, but the
strategy never sits out: with no flat state, chop is traded
continuously, so small per-trade losses compound into a wipeout.
Smoothing demonstrably fails its stated purpose at 1h — it delays
flips without reducing them.

## Mechanism

Heikin-Ashi candles, ha_open and ha_close each smoothed by
EMA(5); long on smoothed close crossing above smoothed open,
short on the cross below; exit on the opposite cross; 2xATR
stop, 2.5xATR trail, 168-bar max hold. All params fixed a priori;
no optimization.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 2,235 trades is an enormous sample — this verdict is not noise.
- Never tune the shipped parameters on this window; no EMA length
  rescues a cross-every-flip design at 1h.
