"""Load the action taxonomy and rules config."""
from __future__ import annotations

import functools
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


@dataclass(frozen=True)
class Label:
    id: str
    phase: str
    description: str
    visual_cues: List[str]
    typical_position: float
    typical_duration: float
    is_step: bool


@dataclass(frozen=True)
class Taxonomy:
    domain: str
    labels: Dict[str, Label]

    @property
    def ids(self) -> List[str]:
        return list(self.labels)

    @property
    def step_ids(self) -> List[str]:
        return [l.id for l in self.labels.values() if l.is_step]


@functools.lru_cache(maxsize=None)
def load_taxonomy(path: str | None = None) -> Taxonomy:
    p = Path(path) if path else CONFIG_DIR / "taxonomy.yaml"
    data = yaml.safe_load(p.read_text())
    labels = {
        lid: Label(
            id=lid,
            phase=d["phase"],
            description=d["description"],
            visual_cues=list(d.get("visual_cues", [])),
            typical_position=float(d.get("typical_position", 0.5)),
            typical_duration=float(d.get("typical_duration", 7)),
            is_step=bool(d.get("is_step", False)),
        )
        for lid, d in data["labels"].items()
    }
    return Taxonomy(domain=data.get("domain", "candle_diy"), labels=labels)


@functools.lru_cache(maxsize=None)
def load_rules(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG_DIR / "rules.yaml"
    return yaml.safe_load(p.read_text())


def prompt_label_reference(tax: Taxonomy) -> str:
    """A compact label reference block to paste into a vision-classification prompt."""
    lines = []
    for l in tax.labels.values():
        star = "step" if l.is_step else "aux "
        cues = "; ".join(l.visual_cues[:4])
        lines.append(f"- {l.id} [{star}|{l.phase}]: {l.description} Visual cues: {cues}")
    return "\n".join(lines)
