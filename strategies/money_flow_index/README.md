# Money Flow Index

## Mechanism

Gene Quong and Avrum Soudack's Money Flow Index is a
volume-weighted RSI: it weights price momentum by how much
volume actually changed hands.

- **Typical price** = (h + l + c) / 3.
- **Raw money flow** = typical price × volume.
- A bar's flow is **positive** when its typical price rose
  vs the prior bar, **negative** when it fell; unchanged
  bars contribute to neither sum.
- **MFI(14)** = 100 − 100 / (1 + positive-14 / negative-14),
  on a 0–100 scale. All-inflow window → 100; flat window →
  50 (neutral).

- **Long entry:** MFI crosses back above 20 from below
  (oversold recovery — the turn, not the touch, so a market
  sliding deeper into oversold territory does not keep
  re-entering).
- **Short entry:** MFI crosses back below 80 from above
  (overbought fade).
- **Exit:** MFI crosses the 50 midline against the position
  (long exits below 50, short exits above 50).

## Entry / exit rules

- Long entry: MFI cross above 20 from below.
- Short entry: MFI cross below 80 from above.
- Long exit: MFI cross below 50. Short exit: MFI cross above 50.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 120-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Money Flow Index (MFI), StockCharts ChartSchool (Gene Quong
and Avrum Soudack)
https://school.stockcharts.com/doku.php?id=technical_indicators:money_flow_index_mfi
— verified: typical price, raw money flow, positive/negative
flow split, 14-period default, 80/20 overbought/oversold.

## Honest caveats

- The backtest (see BACKTEST.md) is a loser: −$3,626
  combined over 382 trades, losing on all three coins
  (PF 0.77–0.80), despite a respectable-looking 39.0% win
  rate — the average loss is simply larger than the average
  win, and 276 of 382 exits are stops. Volume-weighted
  mean reversion does not pay on 1h crypto in this window:
  oversold recoveries keep recovering downward.
- Volume caveat: the v column is Hyperliquid venue volume,
  not whole-market dollar volume, so MFI here reads one
  venue's flow.
- Paper/backtest only. Nothing here touches live execution.
