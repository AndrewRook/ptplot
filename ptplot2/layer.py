from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ptplot import PTPlot


class Layer(ABC):

    @abstractmethod
    def __radd__(self, ptplot: PTPlot):
        pass
