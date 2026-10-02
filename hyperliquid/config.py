#!/usr/bin/env python3
"""Config loading + validation for the Hyperliquid module.

Mirrors the convention of the repo's main engine: `live_trading` must be
an explicit boolean and is never inferred. Any validation failure exits
non-zero with a loud message rather than starting in a half-configured
state.
"""
from __future__ import annotations

import json
import sys


def _fail(msg: str) -> None:
    print(f"hyperliquid config error: {msg}", file=sys.stderr)
    sys.exit(2)


def _need(d: dict, key: str, typ, where: str):
    if key not in d:
        _fail(f"missing {where}.{key}")
    v = d[key]
    if not isinstance(v, typ):
        _fail(f"{where}.{key} must be {typ.__name__}, got {type(v).__name__}")
    return v


def load_config(path: str) -> dict:
    """Load and validate the config file. Returns the parsed dict."""
    try:
        with open(path) as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        _fail(f"cannot read {path}: {e}")

    h = cfg.get("hyperliquid")
    if not isinstance(h, dict):
        _fail("missing [hyperliquid] section")

    for k in ("info_url", "ws_url", "exchange_url"):
        _need(h, k, str, "hyperliquid")

    live = h.get("live_trading")
    if not isinstance(live, bool):
        _fail("hyperliquid.live_trading must be an explicit boolean "
              "(true/false); refusing to start because live mode is "
              "never inferred")

    m = _need(h, "mirror", dict, "hyperliquid")
    for k in ("multiplier", "max_position_usd", "max_notional_per_trade_usd",
              "slippage_buffer_pct", "max_leverage", "reconcile_interval_s"):
        v = _need(m, k, (int, float), "hyperliquid.mirror")
        if v < 0:
            _fail(f"hyperliquid.mirror.{k} must be >= 0")
    if m["multiplier"] <= 0:
        _fail("hyperliquid.mirror.multiplier must be > 0")
    wl = _need(m, "coin_whitelist", list, "hyperliquid.mirror")
    if not all(isinstance(c, str) for c in wl):
        _fail("hyperliquid.mirror.coin_whitelist must be a list of strings")

    k = _need(h, "kelly", dict, "hyperliquid")
    _need(k, "enabled", bool, "hyperliquid.kelly")
    for key in ("fraction", "rolling_closes", "min_closes"):
        _need(k, key, (int, float), "hyperliquid.kelly")
    if not 0 < k["fraction"] <= 1:
        _fail("hyperliquid.kelly.fraction must be in (0, 1]")

    s = _need(h, "scorer", dict, "hyperliquid")
    for key in ("mirror_score_threshold", "fade_score_threshold",
                "min_closed_trades", "cluster_window_s",
                "cluster_min_coentries"):
        _need(s, key, (int, float), "hyperliquid.scorer")
    if not s["fade_score_threshold"] < s["mirror_score_threshold"]:
        _fail("scorer fade threshold must be below the mirror threshold")
    w = _need(s, "weights", dict, "hyperliquid.scorer")
    if abs(sum(w.values()) - 100) > 1e-9:
        _fail("hyperliquid.scorer.weights must sum to 100")

    e = _need(h, "exits", dict, "hyperliquid")
    for key in ("stop_loss_pct", "take_profit_pct", "max_hold_seconds"):
        v = _need(e, key, (int, float), "hyperliquid.exits")
        if v <= 0:
            _fail(f"hyperliquid.exits.{key} must be > 0")

    r = _need(h, "risk", dict, "hyperliquid")
    _need(r, "daily_max_loss_usd", (int, float), "hyperliquid.risk")
    _need(r, "kill_switch_file", str, "hyperliquid.risk")
    if r["daily_max_loss_usd"] <= 0:
        _fail("hyperliquid.risk.daily_max_loss_usd must be > 0")

    p = _need(h, "paper", dict, "hyperliquid")
    for key in ("paper_trades_csv", "decision_log", "shadow_csv",
                "state_file"):
        _need(p, key, str, "hyperliquid.paper")
    g = _need(p, "gate", dict, "hyperliquid.paper")
    _need(g, "min_closed_trades", int, "hyperliquid.paper.gate")
    _need(g, "min_total_pnl_usd", (int, float), "hyperliquid.paper.gate")

    return cfg
