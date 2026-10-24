# Order Block Retest — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,335 bars, 2026-03-14 22:00 UTC →
2026-10-22 23:00 UTC; HYPE 5,333 bars, 2026-03-15 00:00 UTC →
2026-10-22 23:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: 3-bar >= 1.5xATR displacement, last
opposite-color candle as block, retest entry within 48 bars,
block-violation / opposite-displacement exits, 2xATR stop, 2xATR
chandelier trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 97 | 26.8% | -$908 | -9.1% | -1.20 | -16.5% | -$9.36 | 0.76 |
| ETH | 89 | 32.6% | -$35 | -0.4% | +0.01 | -10.9% | -$0.39 | 0.99 |
| HYPE | 102 | 35.3% | -$203 | -1.8% | -0.19 | -10.2% | -$1.99 | 0.93 |
| **Combined** | **288** | **31.6%** | **-$1,146** | — | — | — | -$3.98 | — |

Fees: BTC $991, ETH $765, HYPE $464 (total $2,220).
Exits: ~68% harness stops (BTC 65/97, ETH 60/89, HYPE 69/102),
the rest signal exits (block violation / opposite displacement);
the 96-bar max hold never binds.

## Verdict: a mild loser — no edge, but no blowup either

Combined -$1,146 across 288 trades, all three legs at or below
zero (PF 0.76 / 0.99 / 0.93), with ETH essentially exactly flat
(-$35 on 89 trades, PF 0.99). This is the honest middle outcome:
the retest level is not obviously respected — two-thirds of
trades still end at the harness stop — but it is not obviously
disrespected either. The win rate (31.6%) with a ~1:1-ish payoff
profile is just short of breakeven, and the fee load ($2,220)
exceeds the total loss, so gross of fees the strategy is roughly
flat.

Two readings are both consistent with the numbers. The generous
one: displacement origins carry a weak memory effect that a
tighter entry (e.g., requiring a rejection wick at the block
rather than any close inside) might sharpen. The harsh one: a
level formed by a single candle's range is too thin a level —
any close inside a one-candle range is close to noise, and the
48-bar expiry plus one-entry-per-block rules keep the sample
small (288 trades in seven months across three coins). Either
way, as specified there is nothing to trade here: the edge, if it
exists at all, is smaller than the fee load.

Honest read: not tradeable as specified. If revisited, the first
change to test is entry quality (wick rejection at the block,
not a passive close inside), validated on walk-forward data, not
this window (see CALIBRATION.md: no in-sample tuning was
performed).

## Mechanism

3-bar displacement >= 1.5xATR(14); block = range of the last
opposite-color candle before the leg (scan back <= 20 bars);
enter on a close back inside the block within 48 bars of
displacement, in the displacement direction, one entry per block;
exit on block violation or opposite displacement. 2xATR stop,
2xATR chandelier trail, 96-bar max hold. All params fixed a
priori; no optimization.

Source: ICT (Inner Circle Trader) Smart Money Concepts — order
blocks (https://www.youtube.com/@InnerCircleTrader).

## Limitations

- Single 7-month crypto window; 288 trades is a thin sample for a
  level-respect thesis.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
