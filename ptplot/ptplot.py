from __future__ import annotations

import itertools
import pandas as pd
import patsy

from bokeh.plotting import figure
from bokeh.layouts import layout
from bokeh.models import Slider
from typing import TYPE_CHECKING, List, Optional

from ptplot.animation import Animation
from ptplot.core import _Metadata

if TYPE_CHECKING:
    from ptplot.core import Layer


class PTPlot:
    def __init__(self, data: pd.DataFrame, pixel_height: Optional[int] = 400):
        self.data = data
        self.pixel_height = pixel_height

        self.layers: List[Layer] = []

    @property
    def faceting(self):
        mapper = self._get_attribute_from_layers("faceting")
        return mapper if mapper is not None else lambda data: [(None, data)]

    @property
    def aesthetics(self):
        mapper = self._get_attribute_from_layers("map_aesthetics")
        return mapper if mapper is not None else lambda data: [(data, _Metadata())]

    @property
    def animation_layer(self):
        layer_to_return = None
        for layer in self.layers:
            if isinstance(layer, Animation):
                if layer_to_return is None:
                    layer_to_return = layer
                else:
                    raise ValueError("Only one Animation layer can be used for a given visualization")
        return layer_to_return

    def _get_attribute_from_layers(self, attribute_name):
        attribute = None
        for layer in self.layers:
            if hasattr(layer, attribute_name):
                if attribute is None:
                    attribute = getattr(layer, attribute_name)
                else:
                    raise ValueError(f"Multiple layers have {attribute_name} methods")
        return attribute

    def __add__(self, layer: Layer) -> PTPlot:
        layer.__radd__(self)
        self.layers.append(layer)

        return self  # Allows method chaining

    def draw(self):

        # Extract all mappings set by each layer, then prune duplicates
        mappings = itertools.chain(*[layer.get_mappings() for layer in self.layers])
        mappings = set(mappings)
        # make a dataframe where each mapping is a new column, named based on the mapping
        mapping_data = pd.DataFrame({mapping: _apply_mapping(self.data, mapping) for mapping in mappings})

        # If animation, sort the data by the frame column
        if self.animation_layer is not None:
            mapping_data = mapping_data.sort_values(self.animation_layer.frame_mapping)

        facets = self.faceting(mapping_data)
        figures = []
        animations = []
        for (facet_name, facet_data) in facets:
            figure_object = figure(sizing_mode="scale_both", height=self.pixel_height)
            figure_object.x_range.range_padding = figure_object.y_range.range_padding = 0
            figure_object.x_range.bounds = figure_object.y_range.bounds = "auto"
            figure_object.xgrid.visible = False
            figure_object.ygrid.visible = False
            for data_subset, metadata in self.aesthetics(facet_data):
                for layer in self.layers:
                    layer_animation = layer.draw(self, data_subset, figure_object, metadata)
                    if layer_animation is not None:
                        animations += layer_animation
            figure_object.legend.click_policy = "mute"
            figures.append(figure_object)

        widgets = []
        # TODO: could this be handled by using bokeh's tagging functionality?
        # Probably could, by storing the closure with the plot
        if self.animation_layer is not None:
            min_frame = mapping_data[self.animation_layer.frame_mapping].min()
            max_frame = mapping_data[self.animation_layer.frame_mapping].max()
            slider = Slider(start=min_frame, end=max_frame, value=min_frame, step=1, title="Frame")
            widgets.append(slider)
            for animation in animations:
                callback = animation(self.animation_layer.frame_mapping, min_frame)
                slider.js_on_change("value", callback)
        rows = [figures] if len(widgets) == 0 else [figures, widgets]
        return layout(rows)


def _apply_mapping(
    data: pd.DataFrame,
    mapping: str,
):
    if mapping in data.columns:
        return data[mapping].copy(deep=True)

    processed_string_data = patsy.dmatrix(
        f"I({mapping}) - 1", data, NA_action=patsy.NAAction(NA_types=[]), return_type="dataframe"
    )

    final_data = (
        processed_string_data[processed_string_data.columns[0]]
        if len(processed_string_data.columns) == 1  # pure arithmetic
        else processed_string_data[processed_string_data.columns[1]].astype(bool)  # conditional
    )
    final_data.name = mapping  # Have to explicitly assign the mapping as the name
    return final_data
