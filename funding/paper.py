"""Paper-mode runner: one hourly step of the funding farm.

Pipeline per step:
    fetch current funding -> fetch histories -> rank -> top candidates ->
    decide (open/close/switch) -> size -> apply to ledger -> accrue funding

Pure enough to drive from the backtest (inject histories + marks) and from
a live cron (fetch from the API). No real orders — paper only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from . import ranking as ranking_mod
from . import strategy as strategy_mod
from .api import FundingBar, FundingSnapshot, fetch_current_funding, fetch_funding_history
from .config import FarmConfig, DEFAULT_CONFIG
from .ledger import Ledger
from .ranking import rank_coins, top_candidates
from .sizing import size_positions
from .strategy import Position


@dataclass
class FarmState:
    ledger: Ledger
    positions: Dict[str, Position] = field(default_factory=dict)  # strategy-side view
    paused: bool = False


def new_farm(cfg: FarmConfig = DEFAULT_CONFIG) -> FarmState:
    return FarmState(ledger=Ledger(equity=cfg.farm_capital))


def step(
    state: FarmState,
    snapshots: List[FundingSnapshot],
    histories: Dict[str, List[FundingBar]],
    marks: Dict[str, float],
    cfg: FarmConfig = DEFAULT_CONFIG,
) -> List[dict]:
    """Run one hourly step. Returns the actions taken."""
    if state.paused:
        # Still accrue funding on open positions while paused.
        for coin, pos in list(state.positions.items()):
            snap = next((s for s in snapshots if s.coin == coin), None)
            if snap is not None:
                state.ledger.accrue_funding(coin, snap.funding_hr)
                pos.age_hours += 1.0
        return [{"kind": "paused"}]

    ranked = rank_coins(histories, cfg)
    candidates = top_candidates(ranked, cfg)
    notionals = size_positions(candidates, cfg)

    actions = strategy_mod.decide(ranked, state.positions, cfg)
    taken: List[dict] = []
    for a in actions:
        if a.kind == "open":
            mark = marks.get(a.coin, 0.0)
            n = notionals.get(a.coin, 0.0)
            if n <= 0 or mark <= 0:
                continue
            state.ledger.open(a.coin, n, mark, cfg.entry_threshold_hr,
                              cfg.perp_taker_fee, cfg.spot_fee)
            state.positions[a.coin] = Position(a.coin, n, cfg.entry_threshold_hr)
            taken.append({"kind": "open", "coin": a.coin,
                          "notional": n, "reason": a.reason})
        elif a.kind == "close":
            mark = marks.get(a.coin, 0.0)
            if a.coin in state.positions and mark > 0:
                row = state.ledger.close(a.coin, mark,
                                         cfg.perp_taker_fee, cfg.spot_fee)
                del state.positions[a.coin]
                taken.append({"kind": "close", "coin": a.coin, **row,
                              "reason": a.reason})
        elif a.kind == "switch":
            mark_new = marks.get(a.coin, 0.0)
            mark_old = marks.get(a.from_coin, 0.0)
            if a.from_coin in state.positions and mark_new > 0 and mark_old > 0:
                state.ledger.close(a.from_coin, mark_old,
                                   cfg.perp_taker_fee, cfg.spot_fee)
                del state.positions[a.from_coin]
                state.ledger.open(a.coin, a.notional, mark_new,
                                  cfg.entry_threshold_hr,
                                  cfg.perp_taker_fee, cfg.spot_fee)
                state.positions[a.coin] = Position(a.coin, a.notional,
                                                   cfg.entry_threshold_hr)
                taken.append({"kind": "switch", "coin": a.coin,
                              "from": a.from_coin, "reason": a.reason})
        # "hold" needs no action

    # Accrue one hour of funding on whatever is open now.
    for coin in list(state.positions.keys()):
        snap = next((s for s in snapshots if s.coin == coin), None)
        if snap is not None:
            state.ledger.accrue_funding(coin, snap.funding_hr)
            state.positions[coin].age_hours += 1.0

    return taken
