# RSI extreme-edge — Calibration

Shipped the author's parameters: RSI(14), 90/10 levels, 1.5xATR(14) stop,
1.5xSL target, 72-bar max hold.

## Sweep: RSI levels × stop multiple (target = 1.5 × stop)

Same data, costs, and risk as BACKTEST.md. Combined net PnL over BTC+ETH+HYPE:

| Levels | stop | BTC (tr/net $) | ETH (tr/net $) | HYPE (tr/net $) | Combined net $ |
|---|---|---|---|---|---|
| 90/10 | 1.0x | 1 / -113 | 2 / +30 | 1 / +145 | +62 |
| 90/10 | 1.5x | 1 / -109 | 2 / +36 | 1 / -103 | -176 |
| 90/10 | 2.0x | 1 / -107 | 2 / +39 | 1 / -102 | -170 |
| 85/15 | 1.0x | 10 / -397 | 7 / -56 | 5 / -375 | -828 |
| 85/15 | 1.5x | 9 / -241 | 7 / -23 | 5 / -288 | -551 |
| 85/15 | 2.0x | 9 / -348 | 7 / -6 | 5 / -267 | -620 |
| 95/5 | 1.0x | 0 / 0 | 1 / -107 | 0 / 0 | -107 |
| 95/5 | 1.5x | 0 / 0 | 1 / -104 | 0 / 0 | -104 |
| 95/5 | 2.0x | 0 / 0 | 1 / -103 | 0 / 0 | -103 |

Loosening to 85/15 buys 21 trades — and loses on all three coins. Tightening
to 95/5 leaves a single trade. There is no parameter region with a stable,
positive edge; every number here is sample-size noise.

## Structural stop vs ATR stop (author's alternative)

Re-ran all 4 setups with the stop beyond the excursion extreme (shorts:
highest high since RSI first crossed 90 + 0.25 ATR; longs mirrored),
same 1.5xSL target and 72-bar hold, standalone loop with identical costs:

| Coin | ATR 1.5x stop | Structural stop |
|---|---|---|
| BTC | 1 trade, -$109 | 1 trade, -$111 |
| ETH | 2 trades, +$36 | 2 trades, +$19 |
| HYPE | 1 trade, -$103 | 1 trade, +$145 |

One trade flipping sign on HYPE (+$145) is luck, not evidence. With 1–2
trades per coin there is no basis to prefer either stop — reported both,
shipped the author's ATR rule.
