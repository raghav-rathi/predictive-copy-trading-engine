# Heikin Ashi ADX — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: HA bar colour + ADX(14) > 25 with
the DI lines agreeing; exit on HA flip or ADX < 20; 2xATR
stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 565 | 20.0% | -$7,277 | -72.8% | -7.45 | -73.0% | -$12.88 | 0.41 |
| ETH | 562 | 26.3% | -$6,063 | -60.7% | -4.99 | -61.0% | -$10.79 | 0.53 |
| HYPE | 497 | 27.4% | -$4,622 | -46.2% | -4.08 | -47.6% | -$9.30 | 0.60 |
| **Combined** | **1,624** | **24.4%** | **-$17,962** | — | **-7.40** | **-60.2%** | **-$11.06** | **0.51** |

Fees: BTC $3,158, ETH $2,816, HYPE $1,756 (total $7,730).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL. Combined equity ends
at $12,035 on a $30,000 start.

## Verdict: a catastrophic loser — the ADX filter does not save the HA trend

Combined −$17,962 on 1,624 trades (PF 0.51, Sharpe −7.40)
loses 60% of the combined equity, and every coin loses
heavily: BTC −72.8% (Sharpe −7.45, MaxDD −73.0%), ETH
−60.7%, HYPE −46.2%. Win rates 20–27% with PF 0.41–0.60
say the system is not just unlucky, it is systematically
wrong: entries are level conditions, so after every exit the
harness re-enters on the next bar of the same HA run — the
strategy chases already-extended moves, and the HA flip that
exits the trade is the same lagging signal that entered it
late. Signal exits dominate (444 / 437 / 424 vs 121 / 125 /
73 stops), so the losses are the strategy's own exits
bleeding out, not the harness stop. ADX > 25 does not
discriminate: in a 1h crypto market, a "strong trend" by ADX
is as often the top of a spike as the start of a run.
Honest read: do not trade this. The combination looks
sensible on paper and loses on every coin.

## Mechanism

Heikin Ashi: ha_close = (o+h+l+c)/4; ha_open = (prev ha_open
+ prev ha_close)/2, seeded with the first real open; ha_high
= max(h, ha_open, ha_close); ha_low = min(l, ha_open,
ha_close). ADX(14) via base.adx gives the ADX line and the
+DI/−DI lines. Long on a bullish HA bar with ADX > 25 and
+DI > −DI; short on a bearish HA bar with ADX > 25 and −DI >
+DI. Exit when the HA bar flips against the position or ADX
falls below 20. The harness 2xATR hard stop / 3xATR
chandelier trail sit behind the HA-flip exit as a safety net
for gap-through moves; 120-bar max hold.

Source: Heikin-Ashi chart —
https://en.wikipedia.org/wiki/Heikin-Ashi_chart (verified via
web search 2026-11-26; confirms ha_close = (o+h+l+c)/4,
ha_open = midpoint of the previous HA open/close, and the
max/min high/low envelope).

## Limitations

- Single ~8.5-month crypto window; the verdict is negative on
  all three coins, so the failure is broad, not coin-specific.
- Level-condition entries re-enter the same trend run after
  every exit; a cross-based entry would trade far less and
  was not tested here.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped ADX thresholds on this window.
