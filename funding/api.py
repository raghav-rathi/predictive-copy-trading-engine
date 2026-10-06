"""Hyperliquid funding data access.

Two sources:
  - metaAndAssetCtxs: current hourly funding rate + mark price per coin.
  - fundingHistory: hourly funding history per coin (for trailing averages).

Pure functions over the HTTP layer so tests can inject fixtures.
"""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .config import FarmConfig, DEFAULT_CONFIG


@dataclass
class FundingSnapshot:
    coin: str
    funding_hr: float      # hourly funding rate, fraction of 1 (e.g. 0.0000125)
    mark_px: float
    time_ms: int


@dataclass
class FundingBar:
    coin: str
    funding_hr: float
    time_ms: int


def _post(url: str, payload: dict, timeout_s: int) -> object:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.load(resp)


def fetch_current_funding(
    cfg: FarmConfig = DEFAULT_CONFIG,
    post: Optional[Callable[[str, dict, int], object]] = None,
) -> List[FundingSnapshot]:
    """Current hourly funding for every perp in the universe."""
    post = post or _post
    data = post(f"{cfg.api_url}/info", {"type": "metaAndAssetCtxs"}, cfg.request_timeout_s)
    meta, ctxs = data[0], data[1]
    out: List[FundingSnapshot] = []
    for asset, ctx in zip(meta["universe"], ctxs):
        try:
            out.append(FundingSnapshot(
                coin=asset["name"],
                funding_hr=float(ctx.get("funding", 0.0) or 0.0),
                mark_px=float(ctx.get("markPx", 0.0) or 0.0),
                time_ms=int(ctx.get("time", 0) or 0),
            ))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def fetch_funding_history(
    coin: str,
    start_ms: int,
    end_ms: int,
    cfg: FarmConfig = DEFAULT_CONFIG,
    post: Optional[Callable[[str, dict, int], object]] = None,
) -> List[FundingBar]:
    """Hourly funding history for one coin between start_ms and end_ms."""
    post = post or _post
    data = post(
        f"{cfg.api_url}/info",
        {"type": "fundingHistory", "coin": coin,
         "startTime": start_ms, "endTime": end_ms},
        cfg.request_timeout_s,
    )
    out: List[FundingBar] = []
    for row in data or []:
        try:
            out.append(FundingBar(
                coin=row["coin"],
                funding_hr=float(row["fundingRate"]),
                time_ms=int(row["time"]),
            ))
        except (KeyError, TypeError, ValueError):
            continue
    return sorted(out, key=lambda b: b.time_ms)


def trailing_avg_funding(bars: List[FundingBar], window_hours: int) -> Optional[float]:
    """Mean hourly funding over the last `window_hours` of bars.

    Returns None when there are fewer than `window_hours` bars — the coin
    is not rankable yet (thin-history guard).
    """
    if len(bars) < window_hours:
        return None
    recent = bars[-window_hours:]
    return sum(b.funding_hr for b in recent) / len(recent)
