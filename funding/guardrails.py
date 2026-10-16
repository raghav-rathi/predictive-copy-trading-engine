"""Guardrails for the funding farm.

The farm's failure mode is a funding regime flip (sustained negative
funding = the farm bleeds carry). These checks run before each hourly step:

  1. Portfolio carry guard: if the trailing 7d realized carry across open
     positions is negative -> pause new entries (existing positions still
     accrue; decide() will exit them on the regime-flip rule).
  2. Drawdown guard: if equity falls more than max_drawdown_pct below the
     peak -> pause everything (close nothing automatically; exits stay rule-
     based, but no new opens).
  3. Single-coin concentration: enforced by sizing (max_weight_per_coin);
     re-checked here as a belt-and-braces assertion.

Checks return a list of human-readable trip messages; empty = clear.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .config import FarmConfig, DEFAULT_CONFIG
from .paper import FarmState


@dataclass
class GuardrailConfig:
    max_drawdown_pct: float = 5.0
    carry_window_hours: int = 168


def check(state: FarmState, peak_equity: float,
          gcfg: GuardrailConfig = GuardrailConfig(),
          cfg: FarmConfig = DEFAULT_CONFIG) -> List[str]:
    trips: List[str] = []
    eq = state.ledger.equity

    if peak_equity > 0:
        dd = (peak_equity - eq) / peak_equity * 100
        if dd >= gcfg.max_drawdown_pct:
            trips.append(f"drawdown {dd:.2f}% >= {gcfg.max_drawdown_pct}% cap")

    if cfg.pause_if_7d_carry_negative:
        # Approximate 7d realized carry by open carry + closed carry of the
        # recent window (ledger tracks cumulative; the paper runner resets
        # the window — see paper runner for windowed accounting).
        carry_7d = state.ledger.open_carry() + state.ledger.closed_carry
        if carry_7d < 0 and state.positions:
            trips.append(f"7d realized carry negative ({carry_7d:.2f})")

    for coin, pos in state.positions.items():
        w = pos.notional / cfg.farm_capital if cfg.farm_capital else 0
        if w > cfg.max_weight_per_coin * 1.05:  # 5% tolerance for rounding
            trips.append(f"{coin} weight {w:.1%} exceeds cap")

    return trips


def apply(state: FarmState, trips: List[str]) -> bool:
    """Pause the farm if any guardrail tripped. Returns paused flag."""
    state.paused = bool(trips)
    return state.paused
