# RSI + MACD Confluence

## Mechanism

Two momentum gauges must agree before entry. RSI(14) crossing its 50 midline marks the momentum-regime change; the MACD histogram's sign requires the trend indicator to agree at that moment. An RSI cross while the histogram still points the other way is filtered out — those are the crosses that most often reverse immediately. The exit is the RSI recross alone, so a position is not held through a full momentum reversal waiting for MACD agreement.

## Entry / exit rules

- **Long entry:** RSI(14) crosses above 50 AND MACD histogram > 0.
- **Short entry:** RSI(14) crosses below 50 AND MACD histogram < 0.
- **Long exit:** RSI(14) crosses back below 50.
- **Short exit:** RSI(14) crosses back above 50.

Signals execute at the next bar's open; one position at a time per coin.

## Risk

2xATR stop, 2.5xATR chandelier trail, no fixed target, 168-bar (7-day) max hold, 1% risk/trade, 3x leverage cap.

## Source

RSI + MACD confluence (J. Welles Wilder; Gerald Appel) — https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-strength-index-rsi

## Honest caveats

- Confluence filters entries but does not fix exits: the RSI recross exit is itself whipsaw-prone, and the strategy still trades 1,039 times.
- Win rates are the worst in the batch (19–27%) — the histogram filter admits crosses late, after the move, and the recross exit cuts winners early.
- HYPE is green (+$1,056, PF 1.11, Sharpe +0.81) but BTC (−$4,030, max DD −43.0%) and ETH (−$2,966) lose heavily; one green leg does not rescue a −$5,940 combined print.
- Single 7-month crypto window; funding unmodeled; next-bar-open execution vs idealized entry.
