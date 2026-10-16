"""Coin ranking by trailing-average funding.

Ranks coins on their N-hour mean funding rate. Positive funding means longs
pay shorts, so the farm shorts the perp — the ranking is descending by the
raw average (most positive first).

Coins with insufficient history are excluded (thin-history guard), never
ranked on a partial window.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .api import FundingBar, trailing_avg_funding
from .config import FarmConfig, DEFAULT_CONFIG


@dataclass
class RankedCoin:
    coin: str
    avg_funding_hr: float
    apr: float               # avg_funding_hr * 24 * 365, simple APR
    history_hours: int


def rank_coins(
    histories: Dict[str, List[FundingBar]],
    cfg: FarmConfig = DEFAULT_CONFIG,
) -> List[RankedCoin]:
    """Rank all coins with enough history by trailing-average funding.

    `histories` maps coin -> hourly funding bars (ascending time).
    """
    ranked: List[RankedCoin] = []
    for coin, bars in histories.items():
        if len(bars) < cfg.min_history_hours:
            continue
        avg = trailing_avg_funding(bars, cfg.ranking_window_hours)
        if avg is None:
            continue
        ranked.append(RankedCoin(
            coin=coin,
            avg_funding_hr=avg,
            apr=avg * 24 * 365,
            history_hours=len(bars),
        ))
    ranked.sort(key=lambda r: r.avg_funding_hr, reverse=True)
    return ranked


def top_candidates(
    ranked: List[RankedCoin],
    cfg: FarmConfig = DEFAULT_CONFIG,
) -> List[RankedCoin]:
    """Coins clearing the entry threshold, capped at max_positions."""
    out = [r for r in ranked if r.avg_funding_hr >= cfg.entry_threshold_hr]
    return out[: cfg.max_positions]
