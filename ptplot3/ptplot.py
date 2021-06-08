from __future__ import annotations

import itertools
import pandas as pd
import patsy

from bokeh.plotting import figure
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from .layer import Layer


class PTPlot:
    def __init__(self, data: pd.DataFrame, pixel_height: Optional[int] = 400):
        self.data = data
        self.pixel_height = pixel_height

        self.team_colors = None

        self.plots = []
        self.widgets = []
        self.layers = []

    def __add__(self, layer: Layer) -> PTPlot:
        layer.__radd__(self)
        self.layers.append(layer)

        return self  # Allows method chaining

    def draw(self):

        # Extract all mappings set by each layer, then prune duplicates
        mappings = itertools.chain(*[
            layer.get_mappings() for layer in self.layers
        ])
        mappings = set(mappings)
        # make a dataframe where each mapping is a new column, named based on the mapping
        mapping_data = pd.DataFrame({
            mapping: _apply_mapping(self.data, mapping)
            for mapping in mappings
        })
        figure_object = figure(sizing_mode="scale_both", height=self.pixel_height)
        figure_object.x_range.range_padding = figure_object.y_range.range_padding = 0
        figure_object.x_range.bounds = figure_object.y_range.bounds = "auto"
        for layer in self.layers:
            layer.draw(self, mapping_data, figure_object)

        return figure_object


def _apply_mapping(
        data: pd.DataFrame, mapping: str,
):
    if mapping in data.columns:
        return data[mapping]

    processed_string_data = patsy.dmatrix(
        f"I({mapping}) - 1",
        data,
        NA_action=patsy.NAAction(NA_types=[]),
        return_type="dataframe"
    )

    final_data = (
        processed_string_data[processed_string_data.columns[0]]
        if len(processed_string_data.columns) == 1 # pure arithmetic
        else processed_string_data[processed_string_data.columns[1]].astype(bool) # conditional
    )
    return final_data