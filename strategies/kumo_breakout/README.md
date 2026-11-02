# Kumo Breakout

The Kumo (cloud) breakout trades only the cloud's edges: a close above the cloud top is a breakout long, a close below the cloud bottom a breakdown short, and re-entering the cloud exits. Unlike the full Ichimoku system this version ignores Tenkan/Kijun crosses and Chikou confirmation — the cloud alone is the filter, which makes the signal rarer and later than a Tenkan cross but less noisy.

## Mechanism

- Senkou A = (Tenkan(9) + Kijun(26)) / 2, shifted 26 bars forward.
- Senkou B = 52-bar midpoint, shifted 26 bars forward.
- Cloud top = max(A, B), bottom = min(A, B); both must exist before a level is traded.

## Entry / exit

- **Long entry:** close crosses above cloud top.
- **Short entry:** close crosses below cloud bottom.
- **Exit:** close crosses back into the cloud (below top for longs, above bottom for shorts). The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Ichimoku Cloud / Kumo breakout:
  https://school.stockcharts.com/doku.php?id=technical_indicators:ichimoku_cloud

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 90 bars
(52 bars for Senkou B + 26-bar shift + margin.).

## Honest limitation

The cloud is 26 bars stale by construction, so breakouts are entered well after the move starts and exits lag the reversal by the same mechanism. In a range, price chops through the cloud edges repeatedly and every re-entry exit pays fees (see BACKTEST.md).

Paper only, no live execution.
