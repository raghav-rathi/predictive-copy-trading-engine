#!/usr/bin/env python3
"""Public board: every proposal, verdict, execution and stop event,
posted in real time with P&L and mood.

Append-only JSONL journal (the source of truth) + a static HTML page
generator (the public board): trades table, per-slime P&L / mood, and
the thoughts feed.
"""
from __future__ import annotations

import html
import json
import os
from datetime import datetime, timezone


class Board:
    def __init__(self, path: str):
        self.path = path
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)

    # -- journal --------------------------------------------------------

    def post(self, event: dict) -> None:
        """Append one event. event["type"] in
        {proposal, verdict, execution, stop, note}."""
        event = {"ts": datetime.now(timezone.utc).isoformat(),
                 **event}
        with open(self.path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def read(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        out = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    # -- render ----------------------------------------------------------

    @staticmethod
    def _mood(pnl: float, trades: int) -> str:
        if trades == 0:
            return "😐 idle"
        if pnl > 0:
            return "😎 hot" if pnl > 50 else "🙂 green"
        if pnl < 0:
            return "🥶 cold" if pnl < -50 else "😟 red"
        return "😐 flat"

    def render_html(self, out_path: str) -> str:
        events = self.read()
        per_slime: dict[str, dict] = {}
        trade_rows: list[dict] = []
        thoughts: list[dict] = []

        for e in events:
            s = e.get("slime", "?")
            st = per_slime.setdefault(
                s, {"realized": 0.0, "trades": 0, "wins": 0})
            t = e.get("type")
            if t == "proposal":
                thoughts.append(e)
            elif t == "execution" and e.get("action") == "close":
                pnl = float(e.get("pnl_usd") or 0)
                st["realized"] += pnl
                st["trades"] += 1
                st["wins"] += 1 if pnl > 0 else 0
                trade_rows.append(e)
            elif t == "execution" and e.get("action") == "open":
                trade_rows.append(e)
            elif t == "stop":
                thoughts.append({**e, "thought":
                                 f"🛑 STOP FIRED: {e.get('reason')} on "
                                 f"{e.get('coin')}"})

        def esc(x) -> str:
            return html.escape(str(x))

        slime_cards = []
        for s, st in sorted(per_slime.items()):
            mood = self._mood(st["realized"], st["trades"])
            wr = (st["wins"] / st["trades"] * 100) if st["trades"] else 0
            slime_cards.append(
                f"<div class='card'><h3>{esc(s)}</h3>"
                f"<div class='mood'>{mood}</div>"
                f"<div>PnL: <b>{st['realized']:+.2f} USD</b></div>"
                f"<div>Trades: {st['trades']} · Win rate: {wr:.0f}%</div>"
                f"</div>")

        rows = []
        for e in trade_rows:
            rows.append(
                "<tr>"
                f"<td>{esc(e.get('ts', '')[:19])}</td>"
                f"<td>{esc(e.get('slime', ''))}</td>"
                f"<td>{esc(e.get('action', ''))}</td>"
                f"<td>{esc(e.get('coin', ''))}</td>"
                f"<td>{esc(e.get('side', ''))}</td>"
                f"<td>{esc(e.get('size_usd', e.get('size', '')))}</td>"
                f"<td>{esc(e.get('entry_px', e.get('exit_px', '')))}</td>"
                f"<td>{esc(e.get('reason', e.get('verdict', '')))}</td>"
                f"<td>{esc(e.get('pnl_usd', ''))}</td>"
                "</tr>")

        feed = []
        for e in reversed(thoughts[-50:]):
            feed.append(
                f"<div class='thought'><b>{esc(e.get('slime', ''))}</b> "
                f"<span class='ts'>{esc(e.get('ts', '')[:19])}</span><br>"
                f"{esc(e.get('thought', ''))}</div>")

        page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Slime Board — paper mode</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;
padding:0 1rem;background:#0d1117;color:#e6edf3}}
.banner{{background:#3b2f04;border:1px solid #9e6a03;padding:1rem;
border-radius:8px;margin-bottom:1.5rem}}
.cards{{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:8px;
padding:1rem;min-width:180px}}
.mood{{font-size:1.5rem;margin:.3rem 0}}
table{{width:100%;border-collapse:collapse;margin-bottom:1.5rem}}
th,td{{border:1px solid #30363d;padding:.4rem .6rem;text-align:left;
font-size:.85rem}}
th{{background:#161b22}}
.thought{{background:#161b22;border:1px solid #30363d;border-radius:8px;
padding:.7rem;margin-bottom:.6rem}}
.ts{{color:#8b949e;font-size:.8rem}}
</style></head><body>
<h1>🟢 Slime Board</h1>
<div class="banner">⚠️ <b>PAPER MODE.</b> Every number below is simulated.
Nothing here is live trading or evidence of live edge.</div>
<h2>Slimes</h2><div class="cards">{"".join(slime_cards) or "no slimes yet"}</div>
<h2>Trades</h2>
<table><tr><th>Time</th><th>Slime</th><th>Action</th><th>Coin</th>
<th>Side</th><th>Size USD</th><th>Price</th><th>Reason</th><th>PnL USD</th></tr>
{"".join(rows) or "<tr><td colspan=9>no trades yet</td></tr>"}</table>
<h2>Thoughts feed</h2>
{"".join(feed) or "<p>no thoughts yet</p>"}
</body></html>"""
        d = os.path.dirname(out_path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(out_path, "w") as f:
            f.write(page)
        return out_path
