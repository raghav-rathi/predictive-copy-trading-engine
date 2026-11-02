# RAVI

Chande's RAVI answers one question — is this market trending or ranging — with one number: the percentage gap between SMA(7) and SMA(65). The classic reading uses +/-0.3% reference lines: crossing the upper line says an uptrend has started, crossing the lower a downtrend, and falling back to zero says the trend is over. This system trades exactly those three events.

## Mechanism

- RAVI = 100 x (SMA(7) - SMA(65)) / SMA(65), in percent.
- Upper reference +0.3, lower reference -0.3, zero = trend end.
- One smoothing only (unlike ADX's two), so it reacts earlier than ADX at the cost of more noise.

## Entry / exit

- **Long entry:** RAVI crosses above +0.3.
- **Short entry:** RAVI crosses below -0.3.
- **Exit:** RAVI reverts to zero. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Range Action Verification Index (Tushar Chande):
  https://www.definedgesecurities.com/library/ravi/

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 80 bars
(65 bars for SMA(65) + ATR/margin.).

## Honest limitation

On 1h crypto bars a 0.3% average gap is small — normal volatility crosses it routinely, so the system enters trends that are just noise around the averages. The 65-bar slow average also means the zero-reversion exit lags the actual turn by days (see BACKTEST.md).

Paper only, no live execution.
