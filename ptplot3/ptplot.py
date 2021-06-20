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

        self.layers = []

    @property
    def faceting(self):
        mapper = self._get_attribute_from_layers("faceting")
        return mapper if mapper is not None else lambda data: (None, data)

    @property
    def team_color_mapping(self):
        mapper = self._get_attribute_from_layers("team_color_mapping")
        return mapper if mapper is not None else lambda _: ("black", "gray")

    @property
    def home_away_mapping(self):
        mapper = self._get_attribute_from_layers("home_away_mapping")
        return mapper if mapper is not None else lambda _: True

    @property
    def ball_mapping(self):
        mapper = self._get_attribute_from_layers("ball_mapping")
        return mapper if mapper is not None else None

    @property
    def ball_marker(self):
        marker = self._get_attribute_from_layers("ball_marker")
        return marker if marker is not None else "circle"

    @property
    def ball_colors(self):
        colors = self._get_attribute_from_layers("ball_colors")
        return colors if colors is not None else ["black", "black"]
    # Need to get ball identifier - assume that it's the same as the team identifier
    # For the layer that sets the team mapping, take an argument that's the ball's name in the data
    # When you make the color mapping determine if it's the ball at that time
    # Still need a way to identify the ball to pass to the draw method...

    def _get_attribute_from_layers(self, attribute_name):
        attribute = None
        for layer in self.layers:
            if hasattr(layer, attribute_name):
                if attribute is None:
                    attribute = layer.attribute_name
                else:
                    raise ValueError(
                        f"Multiple layers have {attribute_name} methods"
                    )
        return attribute

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
        facets = self.faceting(mapping_data)
        for (facet_name, facet_data) in facets:
            figure_object = figure(sizing_mode="scale_both", height=self.pixel_height)
            figure_object.x_range.range_padding = figure_object.y_range.range_padding = 0
            figure_object.x_range.bounds = figure_object.y_range.bounds = "auto"
            ball_groups = (
                (False, facet_data) if self.ball_mapping is None
                else facet_data.groupby(self.ball_mapping)
            )
            for is_ball, ball_group in ball_groups:
                if is_ball is True:
                    colors = self.ball_colors
                    marker = self.ball_marker
                    for layer in self.layers:
                        layer.draw(self, ball_group, figure_object, colors=colors, marker=marker)


        # If animation, sort the data by the frame column
        # Add home/away/ball colors to mapping dataframe? Broadly, how to handle situations where
        # you're plotting lots of players instead of teams?
        # If facets defined, split into facets, then for each facet:
        #     create figure
        #     if ball defined, split into ball/non-ball
        #     if teams defined, split non-ball into teams
        #     for each ball/team:
        #         call draw method for each layer, which:
        #         1. draws whatever it needs to on the provided figure
        #         2. returns a list of the sources and the callback strings
        # If animation is set, create the animation widgets, then for each source + callback string pair:
        #     1. Set the filter to the first frame
        #     2. Connect the callbacks to the animation widgets

        # How to set up a facet for later use? Set instance attributes on PTPlot for each
        # of num_per_row, num_per_col, and facet variable? Make a facet object with that info?

        # How to set up animation? Set instance attributes for all args or an animation object?
        # Maybe make a separate method call for animation?
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