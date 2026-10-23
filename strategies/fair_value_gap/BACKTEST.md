# Fair Value Gap Retest — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in ms),
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-22 23:59 UTC
(ms `[1773446400000, 1792713599000)`): 5,330 bars BTC/ETH, 5,328 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2.0xATR stop, 3x leverage
cap, $10k start, both sides. WARMUP=80 bars.

## Results (shipped config: 3-candle FVG with 1.5xATR(14) displacement,
retest entries, mitigation/opposite-signal exits, 2.0xATR stop,
2.0xATR chandelier trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 180 | 26.7% | -$3,763 | -37.6% | -5.03 | -38.3% | -$20.91 | 0.43 |
| ETH | 150 | 33.3% | -$136 | -1.4% | -0.02 | -11.0% | -$0.90 | 0.98 |
| HYPE | 156 | 30.1% | -$1,542 | -15.4% | -1.83 | -22.0% | -$9.88 | 0.72 |
| **Combined** | **486** | **29.8%** | **-$5,440** | — | — | — | -$11.19 | — |

Fees: BTC $1,623, ETH $1,205, HYPE $759 (total $3,587).

Exit mix: the 2.0xATR hard stop took 115/180 BTC trades, 112/150 ETH
trades, and 100/156 HYPE trades; the rest exited on the mitigation /
opposite-signal exit. By side, shorts lost worse than longs on BTC
(-$2,256 vs -$1,507) and HYPE (-$1,277 vs -$264); ETH longs were
mildly green (+$647) but fully offset by shorts (-$782).

## Verdict: a clean loser on every leg — the mechanization is faithful, the edge is not

No ambiguity here: negative on all three coins, 27–33% win rates,
combined -$5,440 with expectancy -$11.19/trade. The losses are not
fee-bound noise (PF 0.43–0.98 gross of fees is structurally negative).
Three things went wrong, all visible in the diagnostics:

1. **The displacement filter is too weak for 1h crypto.** Zones are
   active on 53–61% of bars — the "imbalance" fires on ordinary
   volatility, not the rare institutional footprints ICT describes.
   1.5×ATR on 1h crypto bars is a normal bar, not displacement.
2. **The retest entry catches falling knives.** Price dips into the
   gap and closes back above (the textbook rejection), then keeps
   going through the far edge — the stop (2×ATR, wide by design)
   absorbs the loss before the mitigation exit can fire. 64–75% of
   trades died on the stop.
3. **Shorts are systematically worse.** The bearish-gap retest loses
   more than the bullish one on two of three coins — dip-buying
   mean reversion beats rally-selling here, but neither is green.

The strategy was implemented exactly as the ICT rule is written
(no-lookahead detection, strict-inequality retest entries,
far-edge exits), so this reads as evidence against the raw
mechanization on 1h crypto, not against the implementation. The
honest next steps — a stricter displacement filter, higher-timeframe
context, or zone-quality ranking — are parameter changes on this
window and are refused here (see CALIBRATION.md).

## Mechanism

Bullish FVG at bar i: `l[i] > h[i-2]` AND `range(i-1) > 1.5×ATR(14)`;
zone `[h[i-2], l[i]]`; bearish mirror. Only the most recent
unmitigated zone per direction; bullish dies on `l < fvg_low`,
bearish on `h > fvg_high`. Long on dip-into-gap + close back above;
exit on mitigation or opposite signal. 2.0xATR stop (approximating
"beyond the far edge"), 2.0xATR chandelier trail, 72-bar max hold.

Sources: https://innercircletrader.net/tutorials/fair-value-gap-trading-strategy/ —
https://www.equiti.com/sc-en/news/trading-ideas/fair-value-gap-fvg-the-complete-guide-for-ict-traders/

## Limitations

- Single 7-month crypto window; 486 trades.
- The 2.0xATR stop is a documented approximation of the ICT "beyond
  the far edge" stop, not the rule itself.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Params fixed a priori; no tuning on this window (see CALIBRATION.md).
