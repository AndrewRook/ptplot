from __future__ import annotations

import numpy as np

from abc import ABC, abstractmethod
from bokeh.models import ColumnDataSource, CDSView, CustomJS, IndexFilter
from typing import TYPE_CHECKING, Iterable, Optional

from .layer import Layer

if TYPE_CHECKING:
    from bokeh.plotting import figure
    from bokeh.models import GlyphRenderer
    from .ptplot import PTPlot
    from .nfl import Metadata
    import pandas as pd


class Positions(Layer):
    def __init__(self, x: str, y:str, frame_filter: Optional[str] = None):
        self.x = x
        self.y = y
        self.frame_filter = frame_filter
        self.callback = FIND_CURRENT_FRAME_CALLBACK

    def get_mappings(self) -> Iterable[str]:
        mappings = [self.x, self.y]

        if self.frame_filter is not None:
            mappings += [self.frame_filter]
        return mappings

    def set_up_animation(self, graphics: GlyphRenderer):
        source = graphics.data_source
        view = graphics.view

        def animate(frame_column, initial_frame):
            initial_indices = np.flatnonzero(source.data[frame_column] == initial_frame)
            view.filters[0].indices = initial_indices
            callback = CustomJS(
                args={"source": source, "view": view, "frame_column": frame_column},
                code=self.callback
            )
            return callback

        return animate

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: Metadata):

        # If you have multiple frames but only want to show one (even in an animation):
        if self.frame_filter is not None:
            data = data[data[self.frame_filter]]
        source = ColumnDataSource(data)

        view = CDSView(
            source=source,
            filters=[IndexFilter(
                np.arange(len(data))
            )]
        )

        if metadata.marker is not None:
            graphics = metadata.marker(bokeh_figure)(
                x=self.x, y=self.y, source=source, view=view,
                muted_alpha=0.3,
                legend_label=metadata.label
            )
        else:
            fill_color, line_color = (
                metadata.color_list if metadata.is_home is True
                else ["white", metadata.color_list[0]]
            )
            graphics = bokeh_figure.circle(
                x=self.x, y=self.y, source=source, view=view,
                fill_color=fill_color, line_color=line_color, radius=1, line_width=2,
                muted_alpha=0.3,
                legend_label=metadata.label
            )
        if self.frame_filter is not None:
            return None
        else:
            return self.set_up_animation(graphics)


FIND_CURRENT_FRAME_CALLBACK = """
var data = source.data;
var filter = view.filters[0];
var indices = [];
for (let i = 0; i < data[frame_column].length; i++) {
    if (data[frame_column][i] == cb_obj.value) {
        indices.push(i);
    }
    // Assumes data is sorted by frame_column
    if (data[frame_column][i] > cb_obj.value) {
        break;
    }
} 
filter.indices = indices;
source.change.emit();
"""