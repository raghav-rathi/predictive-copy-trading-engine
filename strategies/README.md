# Technical Strategy Engine Library

Long/short signal engines on Hyperliquid-style OHLCV data. Each strategy is a
self-contained subpackage with indicators, signal logic, risk config, unit
tests, and an empirical backtest note — all **paper-first**: historical
candles and paper signals only, no live execution anywhere by design.

## Layout

```
strategies/
  base.py        indicator primitives + signal/risk conventions
  data.py        Hyperliquid candle loader (candleSnapshot) + disk cache
  backtest.py    event-driven backtest harness (fees, slippage, funding)
  registry.py    strategy registry
  <slug>/
    indicators.py   add_indicators(df) -> df
    signals.py      add_signals(df) -> df  (long_entry/short_entry/long_exit/short_exit)
    risk.py         RiskConfig (stops, trailing, targets, sizing)
    test_<slug>.py  unit tests on synthetic data (network-free)
    BACKTEST.md     empirical results on real candles + calibration note
```

## Execution model

Signals are computed on bar *i* close and executed at bar *i+1* open (no
lookahead). Risk exits (ATR hard stop, chandelier trailing, ATR target,
max-hold) are checked intrabar and take priority. One position at a time.

Costs: 0.045% taker fee + 0.01% slippage per side; hourly funding accrual
from `fundingHistory` (positive rate = longs pay shorts). Sizing risks 1% of
equity per trade on the hard-stop distance, notional capped at 3x equity.

## Running a backtest

```python
from strategies.data import fetch_candles
from strategies.backtest import run_backtest
from strategies.donchian import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=365)
df = indicators.add_indicators(df)
df = signals.add_signals(df)
res = run_backtest(df, risk.RISK, coin="BTC", interval="1h", warmup=60)
print(res.metrics())
```

## Strategies

See `registry.py` (`list_strategies()`); each `<slug>/BACKTEST.md` carries the
honest numbers — winners and losers both.
