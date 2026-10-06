"""Entry / switch / exit decision rules for the funding farm.

State machine per position:
  - ENTER: a top candidate with no current position -> open short perp + long spot.
  - HOLD: keep while its trailing avg stays above the exit threshold and the
    position is younger than max_hold_days.
  - SWITCH: move capital to a new candidate only when
      (candidate_avg - held_avg) * switch_horizon_hours > 4-leg round-trip cost
    (the djienne rule — churn only when the carry gain pays the switch).
  - EXIT: close both legs when the held coin's trailing avg turns negative
    (funding regime flip) or max hold is exceeded.

Decisions are pure: they take the ranked list and current positions and
return a list of actions. Execution (real or paper) consumes the actions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import FarmConfig, DEFAULT_CONFIG
from .ranking import RankedCoin


@dataclass
class Position:
    coin: str
    notional: float          # USD per leg
    entry_avg_funding_hr: float
    age_hours: float = 0.0


@dataclass
class Action:
    kind: str                # "open" | "close" | "switch" | "hold"
    coin: str
    from_coin: Optional[str] = None   # for switch
    notional: float = 0.0
    reason: str = ""


def four_leg_cost_hr(cfg: FarmConfig) -> float:
    """Round-trip cost of one switch expressed as hourly funding-equivalent.

    4 legs: close perp + close spot + open perp + open spot.
    """
    roundtrip = 2 * (cfg.perp_taker_fee + cfg.spot_fee) + cfg.slippage_buffer
    return roundtrip


def decide(
    ranked: List[RankedCoin],
    positions: Dict[str, Position],
    cfg: FarmConfig = DEFAULT_CONFIG,
) -> List[Action]:
    avg_by_coin = {r.coin: r.avg_funding_hr for r in ranked}
    actions: List[Action] = []

    # 1. Exits first: regime flip or max hold.
    for coin, pos in list(positions.items()):
        avg = avg_by_coin.get(coin)
        max_hold_h = cfg.max_hold_days * 24
        if avg is None or avg < cfg.exit_threshold_hr:
            actions.append(Action("close", coin, reason=(
                "funding regime flip" if avg is not None
                else "coin no longer rankable")))
        elif pos.age_hours >= max_hold_h:
            actions.append(Action("close", coin,
                                  reason=f"max hold {cfg.max_hold_days}d reached"))

    closed = {a.coin for a in actions if a.kind == "close"}
    live = {c: p for c, p in positions.items() if c not in closed}

    # 2. Switches: only when carry gain beats 4-leg costs over the horizon.
    cost = four_leg_cost_hr(cfg)
    for coin, pos in live.items():
        held_avg = avg_by_coin.get(coin, pos.entry_avg_funding_hr)
        for cand in ranked:
            if cand.coin == coin or cand.coin in live:
                continue
            gain = (cand.avg_funding_hr - held_avg) * cfg.switch_horizon_hours
            if gain > cost:
                actions.append(Action(
                    "switch", cand.coin, from_coin=coin, notional=pos.notional,
                    reason=(f"carry gain {gain:.5f} > 4-leg cost {cost:.5f} "
                            f"over {cfg.switch_horizon_hours}h")))
                live.pop(coin)
                live[cand.coin] = Position(cand.coin, pos.notional,
                                           cand.avg_funding_hr)
                break  # one switch per held position per decision

    # 3. Fresh entries into free slots.
    free_slots = cfg.max_positions - len(live)
    for cand in ranked:
        if free_slots <= 0:
            break
        if cand.coin in live or cand.coin in closed:
            continue
        if cand.avg_funding_hr < cfg.entry_threshold_hr:
            continue
        actions.append(Action("open", cand.coin,
                              reason=f"7d avg {cand.avg_funding_hr:.7f}/hr "
                                     f"({cand.apr:.1%} APR) clears entry"))
        free_slots -= 1

    return actions
