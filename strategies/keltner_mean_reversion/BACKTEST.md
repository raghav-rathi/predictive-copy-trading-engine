# Keltner Mean Reversion — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-48 window ms `[1773525600000, 1795788000000)`
(2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC exclusive, last
bar 13:00 UTC): 6,184 bars BTC/ETH, 6,182 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: Keltner EMA(20), ATR(10), k=2.0;
long on a close crossing below the lower band on a bullish
candle, short mirror; exit on a cross back to the midline
or the opposite entry; 2xATR stop, 3xATR trail, 72-bar max
hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 0 | — | $0 | 0.0% | 0.00 | 0.0% | $0.00 | 0.00 |
| ETH | 0 | — | $0 | 0.0% | 0.00 | 0.0% | $0.00 | 0.00 |
| HYPE | 0 | — | $0 | 0.0% | 0.00 | 0.00 | $0.00 | 0.00 |
| **Combined** | **0** | **—** | **$0** | **0.0%** | **0.00** | **0.0%** | **$0.00** | **0.00** |

Fees: $0.00 on all coins. No exits of any kind (no trades).

## Verdict: zero trades in eight months -- the entry as specified is unfireable on 1h crypto

This is not a data or implementation problem: the band
crosses happen, 381 lower-band crosses (BTC 126, ETH 117,
HYPE 138) and 363 upper-band crosses (BTC 111, ETH 114,
HYPE 138) in the window, and the close sits beyond a band
on ~350 bars per coin per side. What never happens is the
candle-direction filter coinciding with a cross: 0 of 381
lower-band crosses are bullish candles, 0 of 363
upper-band crosses are bearish candles. On 24/7 crypto the
open chains to the prior close, so a bar that closes across
a band is by construction a directional bar in the
crossing direction -- a down-cross bar closes below its
open, an up-cross bar above it. The filter asks for the
opposite. The rule is shipped exactly as specified and
reported as zero trades rather than silently relaxed: the
filter was not dropped to make the strategy fire. (A
diagnostic run without the candle filter fires 592 trades
and still loses -$5,296 combined, PF 0.75-0.90 per coin --
so the filter is not hiding a winner; see CALIBRATION.md.)
Honest read: the Keltner fade as specified -- cross plus
same-bar reversal candle -- cannot fire on 1h crypto bars,
and the unfiltered version loses anyway. There is nothing
here to trade.

## Mechanism

EMA(20) midline with ATR(10) bands at 2.0x. Entry is a
close crossing a band (cross-based, so one signal per
crossing) plus the same-bar candle direction (bullish on a
lower-band tag, bearish on an upper-band tag). Exit is a
close crossing back to the midline, or the opposite entry,
behind the house 2xATR stop / 3xATR trail and a 72-bar max
hold. The entry cross and the candle filter are the whole
story: the cross fires regularly, the filter never lets
one through.

Source: Keltner channel strategy --
https://www.loomiai.io/learn/keltner-channel-strategy-backtest/

## Limitations

- Zero trades: no per-coin read generalises, and the
  combined $0 is a statement about the entry rule, not
  about Keltner mean reversion in general.
- The candle filter's impossibility is specific to chained
  opens on 1h bars; on daily bars with real overnight gaps
  the same rule can fire. Nothing in this backtest speaks
  to that timeframe.
- Single ~8.4-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped band multiplier on this window.
