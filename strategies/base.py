"""Shared conventions for strategy engines.

OHLCV DataFrame contract
------------------------
Columns (all float except t):
    t : int   -- bar open timestamp, milliseconds, sorted ascending, unique
    o : float -- open
    h : float -- high
    l : float -- low
    c : float -- close
    v : float -- volume (base asset)

Indicator functions take this frame and return a copy with added columns.
Signal functions take the indicator-augmented frame and return a copy with
boolean columns:
    long_entry   -- enter long
    short_entry  -- enter short
    long_exit    -- exit an open long (strategy-defined exit)
    short_exit   -- exit an open short

Execution convention (no lookahead): a signal generated on bar i (using only
data through bar i's close) is executed at bar i+1's open.

Risk config per strategy lives in strategies/<slug>/risk.py as a RiskConfig.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Indicator primitives (pure pandas/numpy, no TA-Lib dependency)
# ---------------------------------------------------------------------------

def sma(s, n: int):
    return s.rolling(n, min_periods=n).mean()


def ema(s, n: int):
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def true_range(h, l, c):
    import pandas as pd

    prev_c = c.shift(1)
    return pd.concat(
        [h - l, (h - prev_c).abs(), (l - prev_c).abs()], axis=1
    ).max(axis=1)


def atr(h, l, c, n: int = 14):
    """Wilder ATR."""
    tr = true_range(h, l, c)
    return tr.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def rsi(c, n: int = 14):
    """Wilder RSI."""
    delta = c.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    ag = gain.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    al = loss.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    rs = ag / al.replace(0, float("nan"))
    out = 100 - 100 / (1 + rs)
    return out.fillna(100.0 * (ag > 0).astype(float))


def adx(h, l, c, n: int = 14):
    """Wilder ADX with +DI/-DI."""
    import pandas as pd

    up = h.diff()
    dn = -l.diff()
    plus_dm = up.where((up > dn) & (up > 0), 0.0)
    minus_dm = dn.where((dn > up) & (dn > 0), 0.0)
    tr = true_range(h, l, c)
    atr_s = tr.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean() / atr_s
    minus_di = 100 * minus_dm.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean() / atr_s
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, float("nan"))
    out = dx.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    return pd.DataFrame({"adx": out, "plus_di": plus_di, "minus_di": minus_di})


def donchian(h, l, n: int):
    import pandas as pd

    return pd.DataFrame(
        {
            f"donchian_high_{n}": h.rolling(n, min_periods=n).max(),
            f"donchian_low_{n}": l.rolling(n, min_periods=n).min(),
        }
    )


def bollinger(c, n: int = 20, k: float = 2.0):
    import pandas as pd

    mid = sma(c, n)
    sd = c.rolling(n, min_periods=n).std()
    return pd.DataFrame(
        {"bb_mid": mid, "bb_upper": mid + k * sd, "bb_lower": mid - k * sd, "bb_width": 2 * k * sd}
    )


def keltner(h, l, c, ema_n: int = 20, atr_n: int = 10, k: float = 1.5):
    import pandas as pd

    mid = ema(c, ema_n)
    a = atr(h, l, c, atr_n)
    return pd.DataFrame(
        {"kc_mid": mid, "kc_upper": mid + k * a, "kc_lower": mid - k * a}
    )


def macd(c, fast: int = 12, slow: int = 26, signal: int = 9):
    import pandas as pd

    line = ema(c, fast) - ema(c, slow)
    sig = ema(line, signal)
    return pd.DataFrame({"macd": line, "macd_signal": sig, "macd_hist": line - sig})


def supertrend(h, l, c, n: int = 10, k: float = 3.0):
    """Classic Supertrend. Returns direction (+1 up / -1 down) and line."""
    import numpy as np
    import pandas as pd

    a = atr(h, l, c, n)
    hl2 = (h + l) / 2
    basic_ub = hl2 + k * a
    basic_lb = hl2 - k * a
    ub = basic_ub.copy()
    lb = basic_lb.copy()
    direction = pd.Series(np.ones(len(c)), index=c.index)
    final_ub = np.full(len(c), np.nan)
    final_lb = np.full(len(c), np.nan)

    ub_v = basic_ub.to_numpy()
    lb_v = basic_lb.to_numpy()
    c_v = c.to_numpy()
    fub = np.full(len(c), np.nan)
    flb = np.full(len(c), np.nan)
    d = np.ones(len(c))
    for i in range(len(c)):
        if i == 0:
            fub[i] = ub_v[i]
            flb[i] = lb_v[i]
            d[i] = 1
            continue
        fub[i] = ub_v[i] if (ub_v[i] < fub[i - 1] or c_v[i - 1] > fub[i - 1]) else fub[i - 1]
        flb[i] = lb_v[i] if (lb_v[i] > flb[i - 1] or c_v[i - 1] < flb[i - 1]) else flb[i - 1]
        if d[i - 1] == 1:
            d[i] = -1 if c_v[i] < flb[i - 1] else 1
        else:
            d[i] = 1 if c_v[i] > fub[i - 1] else -1
    line = np.where(d == 1, flb, fub)
    return pd.DataFrame({"supertrend": line, "supertrend_dir": d}, index=c.index)


def anchored_vwap(h, l, c, v, t_ms):
    """VWAP anchored to each UTC day. Returns vwap and distance in ATR-free z."""
    import numpy as np
    import pandas as pd

    t = pd.to_datetime(t_ms, unit="ms", utc=True)
    day = pd.Series(t).dt.floor("D").to_numpy()
    tp = (h + l + c) / 3
    cum_pv = (tp * v).groupby(day).cumsum()
    cum_v = v.groupby(day).cumsum()
    vwap = cum_pv / cum_v.replace(0, np.nan)
    return pd.Series(vwap.to_numpy(), index=c.index, name="vwap_day")


def ichimoku(h, l, c, tenkan: int = 9, kijun: int = 26, senkou: int = 52):
    import pandas as pd

    tk = (h.rolling(tenkan, min_periods=tenkan).max() + l.rolling(tenkan, min_periods=tenkan).min()) / 2
    kj = (h.rolling(kijun, min_periods=kijun).max() + l.rolling(kijun, min_periods=kijun).min()) / 2
    sa = ((tk + kj) / 2).shift(kijun)
    sb = (
        (h.rolling(senkou, min_periods=senkou).max() + l.rolling(senkou, min_periods=senkou).min()) / 2
    ).shift(kijun)
    chikou = c.shift(-kijun)
    return pd.DataFrame(
        {
            "tenkan": tk,
            "kijun": kj,
            "senkou_a": sa,
            "senkou_b": sb,
            "chikou": chikou,
        }
    )


def crossed_above(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def crossed_below(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


# ---------------------------------------------------------------------------
# Risk config
# ---------------------------------------------------------------------------

@dataclass
class RiskConfig:
    """Per-strategy risk/exit configuration consumed by the backtest harness."""

    atr_window: int = 14
    stop_atr_mult: float = 2.0      # hard stop distance in ATR
    trail_atr_mult: float | None = 3.0  # chandelier trailing distance (None = off)
    target_atr_mult: float | None = None  # take-profit distance (None = off)
    max_hold_bars: int | None = None  # force exit after N bars (None = off)
    risk_frac: float = 0.01        # fraction of equity risked per trade
    max_leverage: float = 3.0      # notional cap as multiple of equity
    fee_rate: float = 0.00045      # taker fee per side (Hyperliquid base)
    slippage_rate: float = 0.0001  # per side
    allow_longs: bool = True
    allow_shorts: bool = True


@dataclass
class StrategySpec:
    name: str
    slug: str
    description: str
    source_name: str
    source_url: str
    warmup_bars: int
    add_indicators: object = field(repr=False)
    add_signals: object = field(repr=False)
    risk: RiskConfig = field(default_factory=RiskConfig)
