"""Strategy registry: name -> StrategySpec."""

from __future__ import annotations

from .base import StrategySpec

REGISTRY: dict[str, StrategySpec] = {}


def register(spec: StrategySpec) -> StrategySpec:
    if spec.slug in REGISTRY:
        raise KeyError(f"duplicate strategy slug: {spec.slug}")
    REGISTRY[spec.slug] = spec
    return spec


def list_strategies() -> list[dict]:
    return [
        {
            "slug": s.slug,
            "name": s.name,
            "description": s.description,
            "source": f"{s.source_name} ({s.source_url})",
        }
        for s in REGISTRY.values()
    ]
