from __future__ import annotations

import itertools
import pandas as pd
import patsy

from bokeh.plotting import figure
from bokeh.layouts import Column, gridplot, row
from bokeh.models import Slider, Toggle, CustomJS
from typing import TYPE_CHECKING, Callable, List, Optional

from ptplot.animation import Animation
from ptplot.core import _Aesthetics
from ptplot.facet import Facet

if TYPE_CHECKING:
    from bokeh.models import GlyphRenderer
    from ptplot.core import Layer


class PTPlot:
    def __init__(self, data: pd.DataFrame, pixel_height: Optional[int] = 400):
        self.data = data
        self.pixel_height = pixel_height

        self.layers: List[Layer] = []

    @property
    def facet_layer(self):
        layer = self._get_class_instance_from_layers(Facet)
        if layer is None:
            try:
                layer = self._layer
            except AttributeError:
                class DummyFacet(Facet):
                    def faceting(self, data):
                        self.num_col = 1
                        self.num_row = 1
                        return [(None, data)]
                self._layer = DummyFacet("dummy")
                layer = self._layer
        return layer

    @property
    def aesthetics_layer(self):
        layer = self._get_class_instance_from_layers(_Aesthetics)
        if layer is None:
            layer = _Aesthetics()
        return layer

    @property
    def animation_layer(self):
        return self._get_class_instance_from_layers(Animation)

    def _get_class_instance_from_layers(self, class_name):
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

        # Extract all mappings set by each layer, then prune duplicates
        mappings = itertools.chain(*[layer.get_mappings() for layer in self.layers])
        mappings = set(mappings)
        # make a dataframe where each mapping is a new column, named based on the mapping
        mapping_data = pd.DataFrame({mapping: _apply_mapping(self.data, mapping) for mapping in mappings})

        # If animation, sort the data by the frame column
        if self.animation_layer is not None:
            mapping_data = mapping_data.sort_values(self.animation_layer.frame_mapping)

        facets = self.facet_layer.faceting(mapping_data)

        figures = []
        animations: List[Callable[[GlyphRenderer], Callable[[str, int], CustomJS]]] = []
        for (facet_name, facet_data) in facets:
            figure_object = figure(
                sizing_mode="scale_both", height=int(self.pixel_height / self.facet_layer.num_row)
            )
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

        widgets = []
        # TODO: could this be handled by using bokeh's tagging functionality?
        # Probably could, by storing the closure with the plot
        if self.animation_layer is not None:
            min_frame = mapping_data[self.animation_layer.frame_mapping].min()
            max_frame = mapping_data[self.animation_layer.frame_mapping].max()
            play_pause = Toggle(label="► Play", active=False)
            widgets.append(play_pause)
            slider = Slider(start=min_frame, end=max_frame, value=min_frame, step=1, title="Frame")
            play_pause_js = CustomJS(
                args={"slider": slider, "min_frame": min_frame,"max_frame": max_frame},
                code="""
var check_and_iterate = function(){
    var slider_val = slider.value;
    var toggle_val = cb_obj.active;
    if(toggle_val == false) {
        cb_obj.label = '► Play';
        clearInterval(play_pause_loop);
        } 
    else if(slider_val == max_frame) {
        cb_obj.label = '► Play';
        slider.value = min_frame;
        cb_obj.active = false;
        clearInterval(play_pause_loop);
        }
    else if(slider_val !== max_frame){
        slider.value = slider_val + 1;
        }
    else {
    clearInterval(play_pause_loop);
        }
}
if(cb_obj.active == false){
    cb_obj.label = '► Play';
    clearInterval(play_pause_loop);
}
else {
    cb_obj.label = '❚❚ Pause';
    var play_pause_loop = setInterval(check_and_iterate, 100);
};
                """
            )
            play_pause.js_on_change('active', play_pause_js)
            widgets.append(slider)
            for animation in animations:
                callback = animation(self.animation_layer.frame_mapping, min_frame)
                slider.js_on_change("value", callback)
        plot_grid = gridplot(figures, ncols=self.facet_layer.num_col)
        if len(widgets) > 0:
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
