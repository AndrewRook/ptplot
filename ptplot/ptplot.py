from __future__ import annotations

import itertools
import pandas as pd
import patsy

from bokeh.plotting import figure
from bokeh.layouts import Column, gridplot, row
from typing import TYPE_CHECKING, Any, Callable, Iterator, List, Optional, Tuple, TypeVar, Type

from ptplot.animation import Animation
from ptplot.core import _Aesthetics
from ptplot.facet import Facet


if TYPE_CHECKING:
    from bokeh.models import CustomJS
    from ptplot.core import Layer

    layer_type = TypeVar("layer_type", bound=Layer)


class PTPlot:
    """The core plotting object, used as the base for all visualizations.

    Once instantiated, Layers can be added to the plot using the "+" operator.

    Parameters
    ----------
    data : The dataset you want to visualize
    pixel_height : How tall the full visualization should be, in pixels. If facets are used this will
    be the total height of all the facets combined.
    """

    def __init__(self, data: pd.DataFrame, pixel_height: int = 400):
        self.data = data
        self.pixel_height = pixel_height

        self.layers: List[Layer] = []

    @property
    def facet_layer(self) -> Facet:
        layer = self._get_class_instance_from_layers(Facet)
        if layer is None:
            try:
                layer = self._layer
            except AttributeError:

                class DummyFacet(Facet):
                    def faceting(self, data: pd.DataFrame) -> Iterator[Tuple[Any, pd.DataFrame]]:
                        self.num_col = 1
                        self.num_row = 1
                        yield (None, data)

                # Need to use this internal storage for the DummyFacet instance or else you re-instantiate
                # every time you call this property *facepalm*
                self._layer = DummyFacet("dummy")
                layer = self._layer
        return layer

    @property
    def aesthetics_layer(self) -> _Aesthetics:
        layer = self._get_class_instance_from_layers(_Aesthetics)
        if layer is None:
            layer = _Aesthetics()
        return layer

    @property
    def animation_layer(self) -> Optional[Animation]:
        return self._get_class_instance_from_layers(Animation)

    def _get_class_instance_from_layers(self, class_name: Type[layer_type]) -> Optional[layer_type]:
        layer_to_return = None
        for layer in self.layers:
            if isinstance(layer, class_name):
                if layer_to_return is None:
                    layer_to_return = layer
                else:
                    raise ValueError(f"Only one {class_name} layer can be used for a given visualization")
        return layer_to_return

    def __add__(self, layer: Layer) -> PTPlot:
        self.layers.append(layer)
        return self  # Allows method chaining

    def draw(self) -> Column:
        """
        Build the visualization specified by all the added layers.

        Returns
        -------
        The final visualization, which is a Bokeh object that can be rendered
        via any of the common Bokeh methods (e.g. show())
        """

        # Extract all mappings set by each layer, then prune duplicates
        all_mappings = itertools.chain(*[layer.get_mappings() for layer in self.layers])
        unique_mappings = set(all_mappings)
        # make a dataframe where each mapping is a new column, named based on the mapping
        mapping_data = pd.DataFrame({mapping: _apply_mapping(self.data, mapping) for mapping in unique_mappings})

        # If animation, sort the data by the frame column
        if self.animation_layer is not None:
            mapping_data = mapping_data.sort_values(self.animation_layer.frame_mapping)

        facets = self.facet_layer.faceting(mapping_data)

        figures = []
        animations: List[Callable[[str, Any], CustomJS]] = []
        for (facet_name, facet_data) in facets:
            # self.facet_layer.num_row should always be non-null at this point, but it
            # appeases mypy
            num_rows = self.facet_layer.num_row if self.facet_layer.num_row is not None else 1

            figure_object = figure(sizing_mode="scale_both", height=int(self.pixel_height / num_rows))
            figure_object.x_range.range_padding = figure_object.y_range.range_padding = 0
            figure_object.x_range.bounds = figure_object.y_range.bounds = "auto"
            figure_object.xgrid.visible = False
            figure_object.ygrid.visible = False
            figure_object.xaxis.visible = False
            figure_object.yaxis.visible = False
            for data_subset, metadata in self.aesthetics_layer.map_aesthetics(facet_data):
                for layer in self.layers:
                    layer_animation = layer.draw(self, data_subset, figure_object, metadata)
                    if layer_animation is not None:
                        animations += layer_animation
            figure_object.legend.click_policy = "mute"
            figures.append(figure_object)

        plot_grid = gridplot(figures, ncols=self.facet_layer.num_col)
        # TODO: could this be handled by using bokeh's tagging functionality?
        # Probably could, by storing the closure with the plot
        if self.animation_layer is not None:
            widgets = self.animation_layer.animate(mapping_data, animations)
            plot_grid.children.append(row(widgets))
        return plot_grid


def _apply_mapping(
    data: pd.DataFrame,
    mapping: str,
) -> pd.Series:
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
