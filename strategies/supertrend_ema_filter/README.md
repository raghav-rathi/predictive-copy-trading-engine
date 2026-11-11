# Supertrend + EMA(200) Filter

Supertrend(10, 3.0) exactly as in `strategies/supertrend` (Olivier
Seban's ATR trailing band), plus an EMA(200) regime filter. This is
deliberately a filtered variant of the existing supertrend strategy —
precedent: `supertrend_adx_filter`, which gates the same flips on
ADX(14) > 25 instead.

## Rules

- **Supertrend:** ATR(10) band, multiplier 3.0; direction flips
  define trend state (shared `strategies.base.supertrend`).
- **Regime filter:** EMA(200) on the close.
- **Long entry:** Supertrend flips to up (+1) while close > EMA(200).
- **Short entry:** Supertrend flips to down (−1) while close <
  EMA(200).
- **Long exit:** Supertrend flips back to down (regardless of
  EMA(200)).
- **Short exit:** Supertrend flips back to up.
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

The filter gates entries only, never exits: a trade entered in-regime
is exited by the Supertrend flip even if price has since crossed the
EMA(200).

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Olivier Seban, Supertrend (public-domain formula): https://www.updata.co.uk/developers/docs/libmanstrat/supertrend
- Parent strategy in this repo: `strategies/supertrend`

Paper only, no live execution.
