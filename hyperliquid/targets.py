#!/usr/bin/env python3
"""Target loading + single-operator clustering for the Hyperliquid module.

Two jobs:

1. Load `targets.json`: address -> {label, classification, score, stats,
   watch, example}. Classifications follow the repo convention:
   copy / fade / pass. `watch: true` marks positive-but-not-yet-copy
   wallets.

2. Single-operator clustering. Our Robinhood Chain research proved this
   matters: 6 "whales" were one bot fleet behind a single funder EOA.
   A copier that treats clustered wallets as independent over-bets one
   signal 6x. Here, wallets that repeatedly open the same coin within a
   short window are unioned into one operator cluster, and the cluster
   casts a single vote (the highest-scored member's classification and
   parameters win; the copy is sized once, not once per member).

Clustering is union-find over pairwise co-entry counts. An "entry" is a
fill whose dir starts with "Open". Two wallets co-enter when they open
the same coin within `cluster_window_s` of each other; `cluster_min_coentries`
such events union the pair.
"""
from __future__ import annotations

import json
import sys
from itertools import combinations


def load_targets(path: str) -> dict[str, dict]:
    """address(lower) -> target dict. Exits non-zero on malformed files."""
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"targets error: cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)
    out: dict[str, dict] = {}
    for w in data.get("wallets", []):
        addr = str(w.get("address", "")).lower()
        if not addr.startswith("0x") or len(addr) != 42:
            print(f"targets error: bad address {w.get('address')!r} in "
                  f"{path}", file=sys.stderr)
            sys.exit(2)
        out[addr] = {
            "label": str(w.get("label", addr)),
            "classification": str(w.get("classification", "pass")),
            "score": float(w.get("score", 0.0)),
            "watch": bool(w.get("watch", False)),
            "example": bool(w.get("example", False)),
            "stats": w.get("stats") or {},
        }
    return out


def cluster_wallets(fills: list[dict], window_s: float,
                    min_coentries: int) -> list[set[str]]:
    """Union wallets that repeatedly co-enter the same coin.

    Returns clusters of >= 2 addresses (singletons are their own
    implicit cluster and are not returned).
    """
    opens: dict[str, list[tuple[str, float]]] = {}
    for f in fills:
        if not str(f.get("dir", "")).startswith("Open"):
            continue
        user = str(f.get("user", "")).lower()
        coin = str(f.get("coin", ""))
        ts = float(f.get("ts", 0) or 0)
        if user and coin and ts:
            opens.setdefault(user, []).append((coin, ts))

    parent: dict[str, str] = {u: u for u in opens}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    users = list(opens)
    for a, b in combinations(users, 2):
        co = 0
        for coin_a, ts_a in opens[a]:
            for coin_b, ts_b in opens[b]:
                if coin_a == coin_b and abs(ts_a - ts_b) <= window_s:
                    co += 1
                    if co >= min_coentries:
                        break
            if co >= min_coentries:
                break
        if co >= min_coentries:
            union(a, b)

    groups: dict[str, set[str]] = {}
    for u in users:
        groups.setdefault(find(u), set()).add(u)
    return [g for g in groups.values() if len(g) > 1]


def cluster_vote(cluster: set[str], targets: dict[str, dict],
                 mirror_threshold: float) -> dict:
    """One vote for the whole cluster: the highest-scored member decides.

    Returns {"members", "representative", "classification", "score"}.
    A cluster is only COPY if its best member clears the mirror
    threshold; if every member is FADE the cluster is FADE; otherwise
    PASS (the engine does nothing).
    """
    ranked = sorted(cluster,
                    key=lambda u: targets.get(u, {}).get("score", 0.0),
                    reverse=True)
    rep = ranked[0]
    rep_t = targets.get(rep, {})
    score = float(rep_t.get("score", 0.0))
    classes = {targets.get(u, {}).get("classification") for u in cluster}
    if rep_t.get("classification") == "copy" and score >= mirror_threshold:
        cls = "copy"
    elif classes == {"fade"}:
        cls = "fade"
    else:
        cls = "pass"
    return {"members": sorted(cluster), "representative": rep,
            "classification": cls, "score": score}
