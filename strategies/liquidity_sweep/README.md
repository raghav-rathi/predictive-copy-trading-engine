# Liquidity Sweep

## Mechanism

Stops cluster beyond obvious swing levels: sell stops below
swing lows, buy stops above swing highs. A liquidity sweep
is a push through such a level that triggers those stops
and then reverses — the break is a grab, not a breakdown.
The tell is the close: a wick beyond the level that closes
back inside the range is a sweep; a candle that closes
beyond the level and stays there is a genuine breakdown.

- **Levels:** the prior 20-bar swing low (minimum low of
  the previous 20 bars, excluding the current bar) and the
  prior 20-bar swing high (maximum high of the same window).
- **Long entry:** a bar whose low wicks below the prior
  20-bar swing low but closes back above that low — on the
  sweep bar itself, or on the next bar if the sweep bar
  closed below the level and the next bar reclaims it. One
  sweep fires at most once.
- **Short entry:** mirror (high wicks above the prior
  20-bar swing high, close back below it).
- **Exit:** the opposite sweep signal, or the risk layer's
  trailing stop.

## Entry / exit rules

- Long entry: reclaimed low sweep while flat.
- Short entry: reclaimed high sweep while flat.
- Long exit: a reclaimed high sweep while long. Short exit
  mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 120-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Trading Liquidity Sweeps Like a Pro (International Trading
Institute)
https://internationaltradinginstitute.com/blog/liquidity-sweeps-entry-exit-strategies/

## Honest caveats

- The backtest (see BACKTEST.md) is a clear loser (-$4,761
  over 516 trades, all three coins negative, combined
  Sharpe -2.36). The sweep-reclaim pattern, as coded, has
  no edge on 1h crypto in this window.
- 358 of 516 exits are stops: most reclaims do not run far
  enough to beat a 2xATR stop before reversing again.
- Paper/backtest only. Nothing here touches live execution.
