from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from bokeh.plotting import figure
    from .ptplot import PTPlot
    from .nfl import Metadata
    import pandas as pd


class Layer(ABC):

    def get_mappings(self) -> Iterable[str]:
        return []

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: Metadata):
        pass

    def __radd__(self, ptplot: PTPlot):
        pass