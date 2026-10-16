"""Configuration for the delta-neutral funding farm."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FarmConfig:
    # Universe / ranking
    ranking_window_hours: int = 168          # 7d average funding
    min_history_hours: int = 72             # coins with less history are not rankable
    entry_threshold_hr: float = 0.000008    # 0.0008%/hr ~ 7% APR to open
    exit_threshold_hr: float = 0.0          # close when 7d avg turns negative

    # Portfolio construction
    max_positions: int = 2
    farm_capital: float = 10_000.0           # paper allocation for the farm
    max_weight_per_coin: float = 0.25       # cap of farm capital per coin

    # Switching rule (djienne): switch only when carry gain beats 4-leg costs
    switch_horizon_hours: int = 168
    switch_gap_apr_points: float = 12.0     # require ~12 APY-point gap

    # Exits
    max_hold_days: int = 30

    # Costs (conservative)
    perp_taker_fee: float = 0.00035         # per leg
    spot_fee: float = 0.0002                # per leg
    slippage_buffer: float = 0.0002        # per switch, both legs

    # Guardrails
    pause_if_7d_carry_negative: bool = True

    # API
    api_url: str = "https://api.hyperliquid.xyz"
    request_timeout_s: int = 20


DEFAULT_CONFIG = FarmConfig()
