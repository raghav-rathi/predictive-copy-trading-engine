# Negative-Funding Fade

Long the perp the moment its funding rate turns negative — shorts
paying longs means the short side is crowded, and the fade is to be
long into that crowded-short sentiment.

## Mechanism

- `funding_rate` is the hourly Hyperliquid funding rate for the
  coin, merged from the local cache (see Data dependency below).
- `funding_neg_turn` is True on the first bar with `funding_rate
  < 0` after a bar with `funding_rate >= 0`.
- **Long entry** on the turn-negative bar (harness executes at the
  next bar's open).
- **Exit after an 8-bar hold** — the long_exit fires 8 bars after
  the entry signal bar, and the harness `max_hold_bars=8` is the
  backstop for the same exit. The exit is time-based, not
  funding-based: a flip back to positive funding mid-hold does not
  cut the trade short.
- **LONG ONLY.** The source thesis is long-only on negative
  funding; there is no symmetric short leg. `allow_shorts=False`,
  and no short signal is ever emitted.

## Source numbers (Jlabs Digital)

Jlabs tested 8h / 16h / 24h holds since 2020; the **8h hold won**:
Sharpe 0.84, +227.67% total return, max drawdown −14.77%, only 14%
time in market. This strategy ships the 8h hold. The Janorium
variant (long while funding is negative, hold 7 days) is documented
here as **not shipped** — a 7-day hold is a different trade (it
harvests a week of funding payments and rides the regime, not the
turn) and is not what Jlabs' winning test measured.

## Data dependency (read this first)

The OHLCV candles carry no funding series. Funding comes from
Hyperliquid's `fundingHistory` endpoint via the committed helper:

```
python3 strategies/funding_fade/fetch_funding.py [BTC ETH HYPE]
```

It writes `data/funding/{COIN}_1h.csv` (columns `t,funding_rate`,
`t` = hour-open ms, aligned to the candle grid — the API returns
timestamps a few tens of ms past the hour, so each row is floored
to the hour). The CSVs are **local only, never committed**
(`data/funding/` is cache, like `data/candles/`).

`indicators.add_indicators` reads `df.attrs["coin"]` (set by the
backtest driver) and merges that coin's cached CSV. If the cache
file is missing, if `df.attrs` has no coin, or if any candle bar
has no funding row, it raises a clear `ValueError` naming the fix
— it NEVER silently falls back to another coin's series or to
zeros. Tests pass a synthetic funding frame through the
`funding_df=` override, so they stay network-free.

One fetching gotcha, found while building this: the API caps
`fundingHistory` responses at ~500 rows, so 30-day request chunks
silently returned only their first ~500 hours and left ~220h gaps.
`fetch_funding.py` uses 10-day chunks (240h) and the cache now
covers the full window contiguously (6,062 hourly rows per coin,
zero gaps).

## Risk

2xATR stop (a risk overlay, not part of the source — see
CALIBRATION.md), no trail, no target, 8-bar max hold, 1% risk per
trade, 3x leverage cap. WARMUP = 24 bars.

Source: Jlabs Digital, "Dissecting Funding Rate model"
(https://typefully.com/jlabsdigital/dissecting-funding-rate-model-BGOoArs).
