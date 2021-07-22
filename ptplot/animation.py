from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Sequence
from bokeh.models import CustomJS, Slider, Toggle

from ptplot.core import Layer


if TYPE_CHECKING:
    import pandas as pd
    from bokeh.models import Widget


class Animation(Layer):
    def __init__(self, frame_mapping: str):
        self.frame_mapping = frame_mapping

    def get_mappings(self) -> Sequence[str]:
        return [self.frame_mapping]

    def animate(
        self, data: pd.DataFrame, layer_animations: Sequence[Callable[[str, Any], CustomJS]]
    ) -> Sequence[Widget]:
        min_frame = data[self.frame_mapping].min()
        max_frame = data[self.frame_mapping].max()
        play_pause = Toggle(label="► Play", active=False)
        slider = Slider(start=min_frame, end=max_frame, value=min_frame, step=1, title="Frame")
        play_pause_js = CustomJS(
            args={"slider": slider, "min_frame": min_frame, "max_frame": max_frame},
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
                        """,
        )
        play_pause.js_on_change("active", play_pause_js)
        for animation in layer_animations:
            callback = animation(self.frame_mapping, min_frame)
            slider.js_on_change("value", callback)
        return [play_pause, slider]
