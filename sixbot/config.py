"""Reads the LOCKED PARAMETERS block from DESK_RULES.md.

DESK_RULES.md is the single source of truth: every bot imports its operating
parameters from here instead of hardcoding them. Change a rule -> edit the
charter, not the code.
"""
import os
import re

_RULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "DESK_RULES.md")


def _coerce(raw):
    raw = raw.strip()
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    try:
        return float(raw)
    except ValueError:
        return raw


def load_params(path=_RULES_PATH):
    with open(path) as fh:
        text = fh.read()
    m = re.search(r"```params\n(.*?)```", text, re.DOTALL)
    if not m:
        raise RuntimeError("LOCKED PARAMETERS block not found in DESK_RULES.md")
    params = {}
    for line in m.group(1).splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, val = line.split("=", 1)
        params[key.strip()] = _coerce(val)
    return params


PARAMS = load_params()


def get(key):
    return PARAMS[key]
