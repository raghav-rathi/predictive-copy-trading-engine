"""Steps 3-4: activity filter and bot filter.

Step 3 (activity): of the ~20 earliest buyers, typically only a handful are
still trading. Keep wallets with at least one trade inside the lookback
window (default 30 days).

Step 4 (bot filter): bots leave a timing signature — trades spaced seconds
apart. A wallet whose inter-trade gaps cluster in the seconds range is
flagged and excluded; such flow cannot be copied by a human anyway.
"""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field


@dataclass
class ActivityVerdict:
    address: str
    kept: bool
    last_trade_ts: float
    trades_in_window: int
    reason: str = ""


@dataclass
class BotVerdict:
    address: str
    is_bot: bool
    median_gap_s: float
    sub_10s_share: float
    n_trades: int
    reason: str = ""


def filter_active(
    last_trade_by_wallet: dict[str, float],
    trades_in_window: dict[str, int] | None = None,
    days: int = 30,
    now: float | None = None,
) -> tuple[list[ActivityVerdict], list[ActivityVerdict]]:
    """Keep wallets active inside the last ``days`` days.

    Returns (kept, dropped). A wallet with no recorded trades is dropped —
    absence of evidence is treated as inactivity, not as a pass.
    """
    now = now if now is not None else time.time()
    cutoff = now - days * 86400
    trades_in_window = trades_in_window or {}
    kept: list[ActivityVerdict] = []
    dropped: list[ActivityVerdict] = []
    for address, last_ts in last_trade_by_wallet.items():
        n = int(trades_in_window.get(address, 0))
        if last_ts >= cutoff and n > 0:
            kept.append(
                ActivityVerdict(address, True, last_ts, n, "active in window")
            )
        else:
            reason = (
                "no trades in window"
                if last_ts < cutoff
                else "zero recorded trades"
            )
            dropped.append(ActivityVerdict(address, False, last_ts, n, reason))
    return kept, dropped


def trade_intervals(timestamps: list[float]) -> list[float]:
    """Sorted ascending gaps (seconds) between consecutive trades."""
    ts = sorted(t for t in timestamps if t and t > 0)
    return [b - a for a, b in zip(ts, ts[1:]) if b > a]


def bot_verdict(
    address: str,
    timestamps: list[float],
    median_gap_threshold_s: float = 60.0,
    sub_10s_share_threshold: float = 0.5,
    min_trades: int = 5,
) -> BotVerdict:
    """Decide whether a wallet's timing looks like a bot.

    Two independent tripwires:
      * median inter-trade gap below ``median_gap_threshold_s`` (default 60s)
      * more than ``sub_10s_share_threshold`` (default 50%) of gaps under 10s

    Fewer than ``min_trades`` trades is not enough evidence either way, so
    the wallet is kept (not flagged) — thin data must not auto-condemn.
    """
    gaps = trade_intervals(timestamps)
    n = len(timestamps)
    if n < min_trades or not gaps:
        return BotVerdict(
            address=address,
            is_bot=False,
            median_gap_s=float("inf") if not gaps else statistics.median(gaps),
            sub_10s_share=0.0,
            n_trades=n,
            reason=f"only {n} trades: insufficient evidence",
        )
    median_gap = statistics.median(gaps)
    sub_10s = sum(1 for g in gaps if g < 10.0) / len(gaps)
    is_bot = (
        median_gap < median_gap_threshold_s or sub_10s > sub_10s_share_threshold
    )
    reason = (
        f"median gap {median_gap:.1f}s, {sub_10s:.0%} of gaps <10s"
        if is_bot
        else f"human-like pacing: median gap {median_gap:.1f}s"
    )
    return BotVerdict(
        address=address,
        is_bot=is_bot,
        median_gap_s=median_gap,
        sub_10s_share=sub_10s,
        n_trades=n,
        reason=reason,
    )


def filter_bots(
    trades_by_wallet: dict[str, list[float]],
    **kwargs,
) -> tuple[list[BotVerdict], list[BotVerdict]]:
    """Split wallets into (humans, bots) by timing signature."""
    humans: list[BotVerdict] = []
    bots: list[BotVerdict] = []
    for address, timestamps in trades_by_wallet.items():
        verdict = bot_verdict(address, timestamps, **kwargs)
        (bots if verdict.is_bot else humans).append(verdict)
    return humans, bots
