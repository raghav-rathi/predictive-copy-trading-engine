"""Camarilla signals, two modes (parameterizable).

FADE (default): first touch of R3 from below each session -> short, first
touch of S3 from above -> long. One fade attempt per level per session.
Exits at the pivot mid; the hard stop (risk.py) is disaster protection
beyond R4/S4.

BREAKOUT: hourly close beyond R4 (from below) -> long with stop-and-reverse
(exits any short), close below S4 (from above) -> short, same reverse.
Exit when price closes back inside the violated level. One reversal per
session per side.
"""

import numpy as np
import pandas as pd

MODE = "fade"  # or "breakout"


def _first_per_group(mask: pd.Series, groups) -> pd.Series:
    """Keep only the first True per group (one attempt per level/session)."""
    m = mask.fillna(False)
    idx = m[m].index.to_numpy()
    grp = [tuple(g) for g in np.asarray(groups, dtype=object)[m.to_numpy()]]
    seen = set()
    keep = np.zeros(len(idx), dtype=bool)
    for k, g in enumerate(grp):
        if g not in seen:
            seen.add(g)
            keep[k] = True
    out = pd.Series(False, index=mask.index)
    out.loc[idx] = keep
    return out


def _fade(df: pd.DataFrame) -> pd.DataFrame:
    touch_r3 = (df["h"] >= df["cam_R3"]) & (df["h"].shift(1) < df["cam_R3"])
    touch_s3 = (df["l"] <= df["cam_S3"]) & (df["l"].shift(1) > df["cam_S3"])
    lvl = pd.Series("none", index=df.index)
    lvl = lvl.mask(touch_r3.fillna(False), "R3").mask(touch_s3.fillna(False), "S3")
    groups = list(zip(df["sess"].astype(str), lvl))
    short_entry = _first_per_group(touch_r3, groups) & (lvl == "R3")
    long_entry = _first_per_group(touch_s3, groups) & (lvl == "S3")
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = (df["c"] >= df["cam_mid"]).fillna(False)
    df["short_exit"] = (df["c"] <= df["cam_mid"]).fillna(False)
    return df


def _breakout(df: pd.DataFrame) -> pd.DataFrame:
    brk_up = (df["c"] > df["cam_R4"]) & (df["c"].shift(1) <= df["cam_R4"])
    brk_dn = (df["c"] < df["cam_S4"]) & (df["c"].shift(1) >= df["cam_S4"])
    grp_up = list(zip(df["sess"].astype(str), ["up"] * len(df)))
    grp_dn = list(zip(df["sess"].astype(str), ["dn"] * len(df)))
    long_entry = _first_per_group(brk_up, grp_up)
    short_entry = _first_per_group(brk_dn, grp_dn)
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    # stop-and-reverse: a breakout in one direction exits the other side
    df["long_exit"] = (
        ((df["c"] < df["cam_R4"]) & (df["c"].shift(1) >= df["cam_R4"])) | short_entry
    ).fillna(False)
    df["short_exit"] = (
        ((df["c"] > df["cam_S4"]) & (df["c"].shift(1) <= df["cam_S4"])) | long_entry
    ).fillna(False)
    return df


def add_signals(df: pd.DataFrame, mode: str = MODE) -> pd.DataFrame:
    df = df.copy()
    if mode == "fade":
        df = _fade(df)
    elif mode == "breakout":
        df = _breakout(df)
    else:
        raise ValueError(f"bad mode {mode}")
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
