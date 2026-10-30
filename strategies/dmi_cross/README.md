# DMI Cross

## Mechanism

Welles Wilder's Directional Movement system (1978): +DM and
−DM measure how much of each bar's range extends the prior
high (up move) or undercuts the prior low (down move), each
Wilder-smoothed over 14 bars and normalized by smoothed True
Range to give +DI and −DI. ADX is the Wilder-smoothed
absolute DI spread — trend strength, not direction.

- **Long entry:** +DI crosses above −DI while ADX(14) > 20.
- **Short entry:** −DI crosses above +DI while ADX(14) > 20.
- **Exit:** the opposite DI cross (taken even if ADX has
  fallen back below 20 — a crossed DI pair no longer
  supports the open side).
- The ADX > 20 gate is the spec's trend filter (Wilder's own
  no-trend line is ADX < 20; 25 marks a strong trend). It
  gates entries only.

Implementation reuses `strategies.base.adx` — no second
Wilder smoothing implementation exists in this strategy.

## Entry / exit rules

- Long entry: +DI cross above −DI, ADX(14) > 20.
- Short entry: −DI cross above +DI, ADX(14) > 20.
- Long exit: −DI cross above +DI. Short exit mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 120-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Average Directional Index (ADX), StockCharts ChartSchool
(Wilder, New Concepts in Technical Trading Systems, 1978)
https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx
— verified: +DI/−DI from Wilder-smoothed +DM/−DM over 14
bars, ADX from smoothed DX, ADX < 20 = no trend.

## Honest caveats

- The backtest (see BACKTEST.md) is a clear loser: −$4,709
  combined over 552 trades, win rate 25.9%, Sharpe −2.19.
  The DI cross on 1h crypto whipsaws: BTC alone loses
  $3,129 with a 22.6% win rate. The ADX > 20 gate does not
  save it — most entries still die on the 2xATR stop
  (303 of 552 exits are stops).
- Paper/backtest only. Nothing here touches live execution.
