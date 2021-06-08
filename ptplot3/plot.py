from __future__ import annotations

from abc import ABC, abstractmethod
from bokeh.models import ColumnDataSource
from typing import TYPE_CHECKING, Iterable, Optional

from .layer import Layer

if TYPE_CHECKING:
    from bokeh.plotting import figure
    from .ptplot import PTPlot
    import pandas as pd


class Positions(Layer):
    def __init__(self, x: str, y:str, frame_filter: Optional[str] = None):
        self.x = x
        self.y = y
        self.frame_filter = frame_filter
        self.callback = FIND_CURRENT_FRAME_CALLBACK if frame_filter is not None else ""

    def get_mappings(self) -> Iterable[str]:
        mappings = [self.x, self.y]

        if self.frame_filter is not None:
            mappings += [self.frame_filter]
        return mappings

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure):
        #full_source = ColumnDataSource(data)

        # If you have multiple frames but only want to show one:
        if self.frame_filter is not None:
            data = data[data[self.frame_filter]]
        # If there is an animation set
        elif hasattr(ptplot, "animation_column"):
            first_frame = data[ptplot.animation_column].min()
            data = data[data[ptplot.animation_column] == first_frame]
        source = ColumnDataSource(data)
        bokeh_figure.circle(
            x=self.x, y=self.y, source=source,
            fill_color="red", line_color="black", radius=1, line_width=2
        )


FIND_CURRENT_FRAME_CALLBACK = """
var data = source.data;
var full_data = full_source.data;

for (const column in data) {
    data[column] = [];
    for (let i = 0; i < full_data[column].length; i++) {
        if (full_data[frame_column][i] == cb_obj.value) {
            data[column].push(full_data[frame_column][i]);
            break;
        }
    }
}
source.change.emit();
"""