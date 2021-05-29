from __future__ import annotations

import pandas as pd

from bokeh.plotting import figure
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layer import Layer

class PTPlot:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.figure = figure(plot_height=400, sizing_mode="scale_width")
        self.figure.x_range.range_padding = self.figure.y_range.range_padding = 0
        #self.figure = figure()

    def __add__(self, layer: Layer) -> PTPlot:
        layer.__radd__(self)

        return self
