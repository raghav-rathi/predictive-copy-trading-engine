# Order Block Retest — Calibration

All parameters were fixed **a priori** from the ICT/SMC order-block
literature and 1h-bar reasoning — there is no in-sample sweep, so
there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Displacement window | 3 bars | the ICT displacement leg is a fast impulsive move; 3h captures it without absorbing the whole trend |
| Displacement threshold | 1.5xATR | a 3-bar move of 1.5 ATR is large enough to be flow, not noise, but common enough to produce a usable sample |
| Block scan-back | 20 bars | the origin candle is normally the last opposite-color candle just before the leg; 20 bars bounds the search without reaching into unrelated structure |
| Block max age | 48 bars (~2 days) | an order block is a fresh level; after two days the flow that made it has usually been absorbed |
| One entry per block | — | a block that already produced an entry and was exited has shown its hand; re-entering it is chasing |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2xATR | roomy enough for a retest to wick through the block without stopping out on noise |
| Max hold | 96 bars (~4 days) | a retest that hasn't resolved in four days is stale, not a retest |
| Risk | 1% / trade, 3x leverage cap | house standard |

The design bet is that the displacement origin is a level the
market respects on retest. The backtest (BACKTEST.md) finds no
edge there on 1h crypto bars — roughly breakeven before the
verdict that matters (all three legs at or below zero).

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers.
