# Elder Triple Screen — Calibration

Shipped the published parameters: 4h MACD(12,26,9) tide, FI(13)/FI2 wave,
prior-bar break trigger, 2.0xATR(14) protective stop.

## Sweep: MACD(fast,slow) ∈ {(8,17), (12,26), (19,39)} × stop ∈ {1.5, 2.0, 2.5}

Same data, costs, and risk as BACKTEST.md. Combined net PnL over BTC+ETH+HYPE:

| MACD | stop | BTC net $ | ETH net $ | HYPE net $ | Combined net $ | Trades |
|---|---|---|---|---|---|---|
| (8,17) | 1.5 | -4,210 | -2,285 | -3,450 | -9,945 | 1,017 |
| (8,17) | 2.0 | -3,272 | -1,952 | -2,537 | -7,762 | 1,017 |
| (8,17) | 2.5 | -2,848 | -1,598 | -1,712 | -6,158 | 1,017 |
| (12,26) | 1.5 | -4,095 | -2,185 | -4,336 | -10,615 | 1,030 |
| (12,26) | 2.0 | -3,081 | -1,820 | -3,157 | -8,058 | 1,030 |
| (12,26) | 2.5 | -2,672 | -1,432 | -2,335 | -6,440 | 1,030 |
| (19,39) | 1.5 | -3,766 | -2,431 | -4,359 | -10,556 | 1,019 |
| (19,39) | 2.0 | -2,583 | -1,919 | -3,419 | -7,920 | 1,019 |
| (19,39) | 2.5 | -2,204 | -1,530 | -2,660 | -6,394 | 1,019 |

## Verdict: ship the published 12,26,9 / 2.0xATR

Every combination is negative on all three coins; the structure loses, not
the parameters. Wider stops (2.5xATR) lose less everywhere — fewer trades
stopped out in chop — but remain red on all three coins, so no stable
alternative exists to switch to. Shipped Elder's published MACD(12,26,9)
and the 2.0xATR protective stop exactly as documented.
