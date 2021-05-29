from __future__ import annotations

import pandas as pd

from bokeh.plotting import figure
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layer import Layer

class PTPlot:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.figure = figure()

    def __add__(self, layer: Layer):
        layer.__radd__(self)

        return self
