"""Delta-neutral funding farm.

Second, uncorrelated book next to the directional copy engine:
short perp + long spot on the highest 7-day-average-funding coins,
harvesting positive funding while staying price-neutral.

Paper-only. Not wired into the live copy engine.
"""

from .config import FarmConfig, DEFAULT_CONFIG

__all__ = ["FarmConfig", "DEFAULT_CONFIG"]
