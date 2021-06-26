from __future__ import annotations

import numpy as np

from abc import ABC, abstractmethod
from copy import deepcopy
from bokeh.models import ColumnDataSource, CDSView, CustomJS, IndexFilter
from typing import TYPE_CHECKING, Sequence, Optional

from ptplot.core import Layer, _Metadata

if TYPE_CHECKING:
    from bokeh.plotting import figure
    from bokeh.models import GlyphRenderer
    from .ptplot import PTPlot
    import pandas as pd


class Tracks(Layer):
    def __init__(self, x: str, y: str, track_mapping: str, animate: bool = True):
        self.x = x
        self.y = y
        self.track_mapping = track_mapping
        self.animate = animate
        self.callback = FIND_ALL_FRAMES_UP_TO_CURRENT_FRAME

    def get_mappings(self) -> Sequence[str]:
        return [self.x, self.y, self.track_mapping]

    def set_up_animation(self, graphics: GlyphRenderer):
        source = graphics.data_source
        full_source = ColumnDataSource(source.data)

        def animate(frame_column, initial_frame):
            is_in_initial_frame = (source.data[frame_column] <= initial_frame)
            initial_data = {
                column: source.data[column][is_in_initial_frame]
                for column in source.data
            }
            source.data = initial_data

            callback = CustomJS(
                args={"source": source, "full_source": full_source, "frame_column": frame_column},
                code=self.callback
            )
            return callback

        return animate

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata):

        line_color = (
            metadata.color_list[0] if metadata.is_home is True
            else  metadata.color_list[1]
        )
        groups = data.groupby(self.track_mapping)
        all_graphics = []
        for group_name, group_data in groups:
            source = ColumnDataSource(group_data)

            graphics = bokeh_figure.line(
                x=self.x, y=self.y, source=source,
                line_color=line_color, line_width=2,
                muted_alpha=0.3,
                legend_label=metadata.label
            )
            all_graphics.append(graphics)

        if self.animate is False:
            return None
        else:
            return [
                self.set_up_animation(graphics)
                for graphics in all_graphics
            ]


class Positions(Layer):
    def __init__(self, x: str, y: str, frame_filter: Optional[str] = None):
        self.x = x
        self.y = y
        self.frame_filter = frame_filter
        self.callback = FIND_CURRENT_FRAME

    def get_mappings(self) -> Sequence[str]:
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

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata):

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
            return [self.set_up_animation(graphics)]


FIND_CURRENT_FRAME = """
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

FIND_ALL_FRAMES_UP_TO_CURRENT_FRAME = """
var data = source.data;
var full_data = full_source.data
for (const column in data) {
    data[column] = [];
    for (let i = 0; i < full_data[frame_column].length; i++) {
        if (full_data[frame_column][i] <= cb_obj.value) {
            data[column].push(full_data[column][i]);
        }
        // Assumes data is sorted by frame_column
        if (full_data[frame_column][i] > cb_obj.value) {
            break;
        }
    } 
}
source.change.emit();
"""