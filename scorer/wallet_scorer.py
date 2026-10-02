#!/usr/bin/env python3
"""Wallet profitability scorer for Robinhood Chain copy candidates.

Pipeline position: scorer/wallet_scorer.py is the *scoring layer*. It
pulls a wallet's ERC-20 transfer history from the Blockscout API v2
(the explorer API is the data route that works from networks where the
public JSON-RPC blackholes -- see docs/research), pairs buys to sells
FIFO per token, and classifies the wallet:

  COPY -- proven profitable AND structurally copyable (win rate / PnL
          over thresholds, enough closed positions, median hold and
          ticket inside configured bounds);
  FADE -- proven loser (win rate / PnL under thresholds over enough
          closed positions): never follow; the engine may treat its
          buys as exit/avoid signals;
  PASS -- everything else: uncopyable structure (e.g. $10 tickets at
          26-second holds), insufficient data, or no measured edge.
          `watch: true` marks positive-but-not-yet-COPY wallets (our
          research WATCH class: wallets 2 and 4 in the seed file).

Output: data/targets.json, consumed by engine/engine.py.

Method notes (honest version):
  * A "swap" is inferred per transaction: non-quote token received
    while a quote token (USDG / WETH, matched by symbol from explorer
    metadata) left the wallet = buy, cost = the quote leg. Mirror for
    sells. Plain transfers with no quote leg (airdrop, inter-wallet
    moves) are ignored, matching the research method.
  * Multi-token swaps split the quote leg equally across tokens and are
    flagged `shared_leg` in the lot record; the fleet data had few.
  * PnL is reported per quote token, never summed across assets and
    never USD-converted without an observed rate.
  * Partial closes consume FIFO lots pro-rata (the same assumption the
    research flagged on wallet 2's MTA/WAVE estimates); positions with
    unmatched sells are ignored, not scored as wins or losses.

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from datetime import datetime, timezone

QUOTE_SYMBOLS = {"USDG", "WETH", "ETH", "USDC", "USDT"}


# --------------------------------------------------------------------------
# Blockscout API v2 client: pagination + polite rate limiting
# --------------------------------------------------------------------------


class Blockscout:
    def __init__(self, base: str, pace_s: float = 0.35, max_retries: int = 6):
        self.base = base.rstrip("/")
        self.pace_s = pace_s
        self.max_retries = max_retries
        self._last_call = 0.0

    def _get(self, path: str, params: dict) -> dict:
        url = self.base + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            wait = self.pace_s - (time.time() - self._last_call)
            if wait > 0:
                time.sleep(wait)
            req = urllib.request.Request(
                url, headers={"User-Agent": "copytrade-robinhood-scorer/0.1"})
            try:
                self._last_call = time.time()
                with urllib.request.urlopen(req, timeout=45) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code == 429:
                    # The explorer is the only working data route from
                    # some networks; a 429 means slow down, not retry hot.
                    retry_after = e.headers.get("Retry-After") if e.headers else None
                    sleep_s = float(retry_after) if retry_after else min(2 ** attempt * 2, 60)
                    print(f"  429 from explorer; backing off {sleep_s}s", file=sys.stderr)
                    time.sleep(sleep_s)
                    continue
                if e.code in (500, 502, 503, 504):
                    time.sleep(min(2 ** attempt, 30))
                    continue
                raise
            except (urllib.error.URLError, TimeoutError) as e:
                last_err = e
                time.sleep(min(2 ** attempt, 30))
        raise RuntimeError(f"explorer GET failed {path}: {last_err}")

    def token_transfers(self, address: str, max_pages: int = 40):
        """Yield transfer dicts for an address, newest first."""
        params: dict = {"type": "ERC-20"}
        for _ in range(max_pages):
            page = self._get(f"/api/v2/addresses/{address}/token-transfers", params)
            for item in page.get("items", []):
                yield item
            nxt = page.get("next_page_params")
            if not nxt:
                return
            params = {"type": "ERC-20", **{k: str(v) for k, v in nxt.items()}}


# --------------------------------------------------------------------------
# Transfer parsing + FIFO profiler
# --------------------------------------------------------------------------


def _norm(item: dict, wallet: str) -> dict | None:
    tok = item.get("token") or {}
    total = item.get("total") or {}
    dec = int(total.get("decimals") or tok.get("decimals") or 18)
    try:
        raw = int(total.get("value") or 0)
    except (TypeError, ValueError):
        return None
    frm = ((item.get("from") or {}).get("hash") or "").lower()
    to = ((item.get("to") or {}).get("hash") or "").lower()
    if wallet not in (frm, to):
        return None
    return {
        "tx": (item.get("transaction_hash") or "").lower(),
        "block": item.get("block_number"),
        "ts": item.get("timestamp"),
        "token": (tok.get("address_hash") or "").lower(),
        "symbol": tok.get("symbol") or "?",
        "amount": raw / (10 ** dec),
        "direction": "in" if to == wallet else "out",
    }


def parse_ts(ts: str | None) -> float | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def profile_wallet(transfers: list[dict]) -> dict:
    """FIFO-pair swap legs into closed positions + open inventory."""
    by_tx: dict[str, list[dict]] = defaultdict(list)
    for t in transfers:
        by_tx[t["tx"]].append(t)

    events: list[dict] = []  # swap legs in first-seen (newest-first) order
    for tx, legs in by_tx.items():
        ins = [l for l in legs if l["direction"] == "in"]
        outs = [l for l in legs if l["direction"] == "out"]
        quote_in = [l for l in ins if l["symbol"] in QUOTE_SYMBOLS]
        quote_out = [l for l in outs if l["symbol"] in QUOTE_SYMBOLS]
        bought = [l for l in ins if l["symbol"] not in QUOTE_SYMBOLS]
        sold = [l for l in outs if l["symbol"] not in QUOTE_SYMBOLS]
        ts = parse_ts(legs[0]["ts"])
        if bought and quote_out:
            q = quote_out[0]
            share = q["amount"] / len(bought)
            for b in bought:
                events.append({"side": "buy", "token": b["token"],
                               "symbol": b["symbol"], "amount": b["amount"],
                               "quote_symbol": q["symbol"], "quote": share,
                               "ts": ts, "tx": tx,
                               "shared_leg": len(bought) > 1})
        if sold and quote_in:
            q = quote_in[0]
            share = q["amount"] / len(sold)
            for s in sold:
                events.append({"side": "sell", "token": s["token"],
                               "symbol": s["symbol"], "amount": s["amount"],
                               "quote_symbol": q["symbol"], "quote": share,
                               "ts": ts, "tx": tx,
                               "shared_leg": len(sold) > 1})

    # explorer returns newest first; FIFO needs chronological order
    events.sort(key=lambda e: (e["ts"] or 0))

    lots: dict[str, deque] = defaultdict(deque)      # token -> open buy lots
    closed: list[dict] = []
    for e in events:
        if e["side"] == "buy":
            lots[e["token"]].append({
                "symbol": e["symbol"], "amount": e["amount"],
                "quote_symbol": e["quote_symbol"], "cost": e["quote"],
                "ts": e["ts"], "tx": e["tx"]})
            continue
        remaining = e["amount"]
        proceeds_left = e["quote"]
        while remaining > 1e-12 and lots[e["token"]]:
            lot = lots[e["token"]][0]
            take = min(lot["amount"], remaining)
            frac = take / lot["amount"] if lot["amount"] else 0
            cost_part = lot["cost"] * frac
            proceeds_part = e["quote"] * (take / e["amount"]) if e["amount"] else 0
            closed.append({
                "token": e["token"], "symbol": lot["symbol"],
                "quote_symbol": lot["quote_symbol"],
                "pnl": proceeds_part - cost_part,
                "cost": cost_part, "proceeds": proceeds_part,
                "hold_s": (e["ts"] - lot["ts"]) if (e["ts"] and lot["ts"]) else None,
                "ticket": cost_part,
                "buy_tx": lot["tx"], "sell_tx": e["tx"],
                "partial": frac < 0.999 or take < remaining,
            })
            lot["amount"] -= take
            lot["cost"] -= cost_part
            remaining -= take
            proceeds_left -= proceeds_part
            if lot["amount"] <= 1e-12:
                lots[e["token"]].popleft()
        # unmatched sell remainder: buy predates coverage -> unscored

    by_quote: dict[str, float] = defaultdict(float)
    cost_by_quote: dict[str, float] = defaultdict(float)
    wins = 0
    for c in closed:
        by_quote[c["quote_symbol"]] += c["pnl"]
        cost_by_quote[c["quote_symbol"]] += c["cost"]
        if c["pnl"] > 0:
            wins += 1
    holds = [c["hold_s"] for c in closed if c["hold_s"] is not None]
    tickets = [c["ticket"] for c in closed if c["cost"] > 0]
    open_positions = [
        {"token": tok, "symbol": lot["symbol"], "amount": lot["amount"],
         "quote_symbol": lot["quote_symbol"], "cost_open": lot["cost"]}
        for tok, dq in lots.items() for lot in dq if lot["amount"] > 1e-12
    ]
    return {
        "closed_positions": len(closed),
        "wins": wins,
        "win_rate": (wins / len(closed)) if closed else None,
        "realized_pnl_by_quote": dict(by_quote),
        "closed_cost_by_quote": dict(cost_by_quote),
        "median_hold_s": statistics.median(holds) if holds else None,
        "median_ticket": statistics.median(tickets) if tickets else None,
        "open_positions": open_positions,
        "closed": closed,
    }


# --------------------------------------------------------------------------
# Classifier
# --------------------------------------------------------------------------


def classify(profile: dict, th: dict) -> tuple[str, bool, list[str]]:
    """Return (classification, watch, reasons). Thresholds from config."""
    reasons: list[str] = []
    closed_n = profile["closed_positions"]
    pnl_usdg = profile["realized_pnl_by_quote"].get("USDG", 0.0)
    if closed_n < th["min_closed_positions"]:
        # Provisional zone: positive-but-thin records are exactly our
        # research WATCH class; keep them visible but untradeable. (The
        # seed priors for wallets 2/4 stay authoritative until the
        # scorer has seen enough closes to overrule them.)
        return "pass", pnl_usdg > 0, [
            f"insufficient data: {closed_n} closed positions "
            f"< {th['min_closed_positions']} minimum"]
    wr = profile["win_rate"] or 0.0
    hold = profile["median_hold_s"]
    ticket = profile["median_ticket"]

    if wr <= th["fade_max_win_rate"] and pnl_usdg <= th["fade_max_pnl_usdg"]:
        return "fade", False, [f"proven loser: win rate {wr:.0%}, "
                                f"realized {pnl_usdg:+.2f} USDG over {closed_n} closes"]
    copyable = True
    if hold is not None and not (th["copy_min_median_hold_s"] <= hold <= th["copy_max_median_hold_s"]):
        copyable = False
        reasons.append(f"median hold {hold:.0f}s outside copyable band "
                       f"[{th['copy_min_median_hold_s']}, {th['copy_max_median_hold_s']}]s")
    if ticket is not None and ticket < th["copy_min_median_ticket_usdg"]:
        copyable = False
        reasons.append(f"median ticket {ticket:.2f} below copyable floor "
                       f"{th['copy_min_median_ticket_usdg']} (slippage would eat it)")
    if wr >= th["copy_min_win_rate"] and pnl_usdg >= th["copy_min_pnl_usdg"]:
        if not copyable:
            return "pass", True, ["profitable but uncopyable structure"] + reasons
        # A green *closed* record can hide a mountain of unresolved bags
        # (research wallet 2: most capital still open). If open USDG cost
        # dwarfs what has actually been closed, the record is provisional.
        open_cost = sum(p["cost_open"] for p in profile["open_positions"]
                        if p["quote_symbol"] == "USDG")
        closed_cost = profile["closed_cost_by_quote"].get("USDG", 0.0)
        if closed_cost > 0 and open_cost > closed_cost * th["copy_max_open_cost_ratio"]:
            return "pass", True, [
                f"green but provisional: open USDG cost {open_cost:.2f} is "
                f"{open_cost / closed_cost:.1f}x closed cost "
                f"(cap {th['copy_max_open_cost_ratio']}x)"]
        return "copy", False, [f"profitable and copyable: win rate {wr:.0%}, "
                               f"realized {pnl_usdg:+.2f} USDG over {closed_n} closes"]
    if pnl_usdg > 0:
        if copyable:
            return "pass", True, [f"positive but below COPY bar: win rate {wr:.0%}, "
                                  f"realized {pnl_usdg:+.2f} USDG"]
        return "pass", False, ["positive but uncopyable structure"] + reasons
    return "pass", False, [f"no measured edge: win rate {wr:.0%}, "
                           f"realized {pnl_usdg:+.2f} USDG"] + reasons


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def load_json(path: str, default):
    if path and os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def score_wallet(client: Blockscout, address: str, th: dict,
                 max_pages: int) -> dict:
    wallet = address.lower()
    raw = [t for t in (_norm(i, wallet)
                       for i in client.token_transfers(address, max_pages))
           if t is not None]
    profile = profile_wallet(raw)
    cls, watch, reasons = classify(profile, th)
    # closed detail is audit data; keep it out of targets.json (bulky)
    profile = {k: v for k, v in profile.items() if k != "closed"}
    return {"address": address, "classification": cls, "watch": watch,
            "reasons": reasons, "metrics": profile,
            "transfers_seen": len(raw)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--seed", default="data/whales_seed.json",
                    help="candidate seed list (research classifications kept as prior)")
    ap.add_argument("--out", default="data/targets.json")
    ap.add_argument("--wallet", action="append", default=[],
                    help="extra candidate wallet (repeatable)")
    ap.add_argument("--max-pages", type=int, default=40)
    args = ap.parse_args()

    cfg = load_json(args.config, {})
    th = cfg.get("scorer", {}).get("thresholds", {})
    explorer = cfg.get("robinhood", {}).get(
        "explorer_api", "https://robinhoodchain.blockscout.com")
    client = Blockscout(explorer)

    seed = load_json(args.seed, {"wallets": []})
    candidates: dict[str, dict] = {}
    for w in seed.get("wallets", []):
        candidates[w["address"].lower()] = w
    for addr in args.wallet:
        candidates.setdefault(addr.lower(), {"address": addr})

    results = []
    for addr, prior in candidates.items():
        print(f"scoring {addr} ...", file=sys.stderr)
        try:
            r = score_wallet(client, addr, th, args.max_pages)
        except Exception as e:
            print(f"  FAILED {addr}: {e}", file=sys.stderr)
            r = {"address": addr, "classification": "pass", "watch": False,
                 "reasons": [f"scoring failed: {e}"], "metrics": None}
        r["prior_research_class"] = prior.get("classification")
        r["operator_episodes_copied"] = prior.get("episodes_copied")
        results.append(r)

    order = {"copy": 0, "fade": 1, "pass": 2}
    results.sort(key=lambda r: (order[r["classification"]], r["address"]))
    out = {"generated_at": datetime.now(timezone.utc).isoformat(),
           "source": "Blockscout API v2 token-transfers, FIFO pairing",
           "wallets": results}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    for r in results:
        m = r.get("metrics") or {}
        pnl = (m.get("realized_pnl_by_quote") or {}).get("USDG")
        print(f"{r['classification'].upper():4} {r['address']} "
              f"closed={m.get('closed_positions')} win_rate={m.get('win_rate')} "
              f"pnl_usdg={pnl} :: {'; '.join(r['reasons'])}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
