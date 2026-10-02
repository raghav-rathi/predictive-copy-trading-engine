#!/usr/bin/env python3
"""Minimal notifier for the Hyperliquid copy engine.

Events: trade opened, trade closed (with PnL), breaker tripped, errors.
Two backends:

  * "log" (default): JSON lines to stderr. Always works, nothing to
    configure.
  * "telegram": sends to a Telegram chat via the Bot API. Credentials
    come ONLY from the environment at runtime —
    TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID — never from code, config
    files, or logs. If either is absent, the telegram backend degrades
    to the logging backend with a one-time warning. TODO-operator:
    set the env vars on the deployment host (secret manager, not a
    checked-in file).

No credentials are stored, printed, persisted, or embedded here.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


class Notifier:
    def emit(self, event: dict) -> None:
        raise NotImplementedError


class LoggingNotifier(Notifier):
    """JSON lines to stderr. The always-on fallback."""

    def emit(self, event: dict) -> None:
        print(f"[notify {_ts()}] {json.dumps(event, default=str)}",
              file=sys.stderr, flush=True)


class TelegramNotifier(Notifier):
    """Telegram Bot API sender. Env-configured; degrades to logging."""

    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        self._warned = False
        self._fallback = LoggingNotifier()

    def _format(self, event: dict) -> str:
        kind = event.get("kind", "?")
        if kind == "trade_opened":
            return (f"OPEN {event.get('coin')} {event.get('side')} "
                    f"{event.get('size')} @ {event.get('entry_px')} "
                    f"(copy of {event.get('target')})")
        if kind == "trade_closed":
            return (f"CLOSE {event.get('coin')} "
                    f"{event.get('exit_reason')} "
                    f"pnl {float(event.get('pnl_usd', 0)):+.2f} USD")
        if kind == "breaker_tripped":
            return (f"BREAKER {event.get('layer')}: {event.get('reason')} "
                    f"— {event.get('detail', '')}")
        if kind == "error":
            return f"ERROR: {event.get('detail', event)}"
        return json.dumps(event, default=str)

    def emit(self, event: dict) -> None:
        if not (self.token and self.chat_id):
            if not self._warned:
                self._warned = True
                print(f"[notify {_ts()}] telegram backend not configured "
                      f"(TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID unset); "
                      f"falling back to logging", file=sys.stderr, flush=True)
            self._fallback.emit(event)
            return
        try:
            payload = json.dumps({
                "chat_id": self.chat_id,
                "text": self._format(event),
            }).encode()
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15):
                pass
        except Exception as e:  # delivery failure: log, never raise
            print(f"[notify {_ts()}] telegram send failed ({e}); event: "
                  f"{json.dumps(event, default=str)}",
                  file=sys.stderr, flush=True)


def build_notifier(cfg: dict) -> Notifier:
    """Backend from config: paper.notifier.backend = "log"|"telegram"."""
    backend = ((cfg.get("hyperliquid") or {}).get("paper") or {}) \
        .get("notifier", {}).get("backend", "log")
    if str(backend).lower() == "telegram":
        return TelegramNotifier()
    return LoggingNotifier()
