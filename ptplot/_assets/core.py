from dataclasses import dataclass

from typing import Sequence


@dataclass
class Field:
    length: float
    width: float
    lines_markers: Sequence[dict]
    background_color: str
    length_padding: float = 3
    width_padding: float = 5
