# RSI pullback to EMA(50) — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC 6,064 bars, ETH 6,064 bars, HYPE 6,062 bars — HYPE's cache
starts two bars later, at 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: EMA(50) trend filter; RSI(14) dip
below 40 then cross back above 40 in an uptrend — mirror short
on RSI above 60 crossing back below 60 in a downtrend; exit
long on RSI 70 or close below EMA(50), exit short on RSI 30 or
close above EMA(50); 2xATR harness backstop; 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 2 | 0.0% | -$189 | -1.9% | -1.66 | -1.9% | -$94.26 | 0.00 |
| ETH | 1 | 100.0% | +$31 | +0.3% | +0.21 | -1.4% | +$30.85 | inf |
| HYPE | 0 | — | $0 | 0.0% | 0.00 | 0.0% | $0.00 | — |
| **Combined** | **3** | **33.3%** | **-$158** | — | — | — | **-$52.56** | — |

Fees: BTC $22, ETH $8, HYPE $0 (total $30).

## Verdict: no-trade — the EMA filter strangles the setup

Three trades in eight months across three coins, one of them
HYPE with zero trades. That is the finding, and it is reported
as-is: **this backtest cannot validate or invalidate the RSI
pullback thesis**, because the system almost never fired.

- Why so few triggers: the two conditions fight each other. A
  dip deep enough to push RSI(14) below 40 on 1h bars almost
  always also pushes price below EMA(50) — and the moment the
  trend breaks, the armed setup is disarmed (see
  CALIBRATION.md). The synthetic test in the suite shows the
  same thing: a -8/bar dip breaks the EMA and produces no
  entry, while only a shallow -2/bar dip keeps the trend and
  fires. On real 1h crypto, pullbacks are usually violent
  enough to break the 50-bar EMA.
- The three trades that did fire are noise: BTC 0-for-2
  (-$189), ETH 1-for-1 (+$31, profit factor "inf" on a single
  trade — meaningless), HYPE nothing. No statistic here is
  significant; do not quote the -$158 or the per-coin Sharpe
  figures as an edge in either direction.
- The honest read: the system as specified is a
  **no-op on 1h crypto**. The EMA filter does its job too
  well — it screens out the falling knives, and with them
  nearly every setup. Loosening the filter (wider RSI band,
  slower EMA, allowing the dip to break the EMA) would
  manufacture trades, but that would be tuning on this window,
  so we do not do it here.

Stated plainly: the pullback idea is untested by this window,
not disproven. A real verdict would need a slower timeframe
(daily bars, where a 40-RSI dip can happen without breaking a
50-day EMA), a wider RSI band, or more coins.

## Mechanism

Uptrend = close above a rising EMA(50); in an uptrend RSI(14)
dipping below 40 arms the long, and RSI crossing back above 40
while the trend still holds enters. Short mirror in a
downtrend (RSI above 60, cross back below 60). Exit long on
RSI 70 or close below EMA(50); exit short on RSI 30 or close
above EMA(50). No opposite-side flip. All params fixed a
priori; no optimization.

Source: Larry Connors & Linda Raschke, *Street Smarts* (1995),
pullback chapter — https://www.tradingview.com/ideas/
(reference only; implemented from the rules above).

## Limitations

- 3 trades total: no statistic here is significant.
- Single 8-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- The RSI(14) seeding in base.rsi reads 0 on flat/zero-delta
  stretches; harmless here (WARMUP=60 covers it) but noted.
- Never tune the shipped parameters on this window — least of
  all the 40/60 RSI band or the EMA(50) length, which directly
  control how many trades fire.
