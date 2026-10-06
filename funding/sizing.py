"""Position sizing for the funding farm.

Carry-weighted allocation: capital sits where carry is highest, subject to a
per-coin cap. Weights are proportional to each candidate's trailing-average
funding rate (clipped at zero — only positive-carry coins are candidates).

  weight_i = max(avg_i, 0) / sum(max(avg_j, 0))
  notional_i = min(farm_capital * max_weight_per_coin, farm_capital * weight_i)

1x per leg, delta-neutral by construction. No leverage.
"""
from __future__ import annotations

from typing import Dict, List

from .config import FarmConfig, DEFAULT_CONFIG
from .ranking import RankedCoin


def size_positions(
    candidates: List[RankedCoin],
    cfg: FarmConfig = DEFAULT_CONFIG,
) -> Dict[str, float]:
    """Map coin -> USD notional per leg."""
    positive = [c for c in candidates if c.avg_funding_hr > 0]
    if not positive:
        return {}
    total = sum(c.avg_funding_hr for c in positive)
    if total <= 0:
        return {}
    out: Dict[str, float] = {}
    cap = cfg.farm_capital * cfg.max_weight_per_coin
    for c in positive:
        weight = c.avg_funding_hr / total
        out[c.coin] = round(min(cap, cfg.farm_capital * weight), 2)
    return out
