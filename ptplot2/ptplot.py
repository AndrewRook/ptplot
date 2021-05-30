from __future__ import annotations

import pandas as pd

from bokeh.plotting import figure
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .layer import Layer


class PTPlot:
    def __init__(self, data: pd.DataFrame, pixel_height: Optional[int] = 400):
        self.data = data
        self.figure = figure(sizing_mode="scale_both", height=pixel_height)
        self.figure.x_range.range_padding = self.figure.y_range.range_padding = 0
        self.figure.x_range.bounds = self.figure.y_range.bounds = "auto"

    def __add__(self, layer: Layer) -> PTPlot:
        layer.__radd__(self)

        return self
