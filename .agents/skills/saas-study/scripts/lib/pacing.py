"""Randomized pacing helpers driven by stealth profile."""
from __future__ import annotations
import json
import random
import time
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = SKILL_ROOT / "config" / "stealth.json"


def load_profile(name: str | None = None) -> dict:
    cfg = json.loads(CONFIG_PATH.read_text())
    profile_name = name or cfg.get("default_profile", "balanced")
    if profile_name not in cfg["profiles"]:
        raise ValueError(f"Unknown stealth profile: {profile_name}")
    profile = dict(cfg["profiles"][profile_name])
    profile["_name"] = profile_name
    return profile


def jittered_sleep(profile: dict, key: str) -> float:
    """Sleep a randomized duration based on profile[key] = [min, max].

    Optionally adds a 'distraction' pause based on profile.human_distraction_chance.
    Returns the actual sleep duration (for logging).
    """
    rng = profile.get(key)
    if not rng or len(rng) != 2:
        return 0.0
    base = random.uniform(rng[0], rng[1])
    extra = 0.0
    if random.random() < profile.get("human_distraction_chance", 0.0):
        extra = random.uniform(2.0, 8.0)
    total = base + extra
    time.sleep(total)
    return total
