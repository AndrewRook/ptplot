from __future__ import annotations

from bokeh.models import Slider
from typing import TYPE_CHECKING, Iterable, Optional

from .layer import Layer

if TYPE_CHECKING:
    from bokeh.plotting import figure
    from .ptplot import PTPlot
    import pandas as pd


class Animate(Layer):
    def __init__(self, frame: str, frame_label: Optional[str] = None):
        self.frame = frame
        self.frame_label = frame_label

    def get_mappings(self) -> Iterable[str]:
        mappings = [self.frame]
        if self.frame_label is not None:
            mappings.append(self.frame_label)

        return mappings

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure):
        minimum_frame = data[self.frame].min()
        maximum_frame = data[self.frame].max()
        slider = Slider(
            start=minimum_frame, end=maximum_frame, value=minimum_frame, step=1,
            title="frame"
        )
        ptplot.widgets.append(slider)
