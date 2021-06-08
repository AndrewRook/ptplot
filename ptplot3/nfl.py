from __future__ import annotations

import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings

from .layer import Layer
from typing import TYPE_CHECKING, Iterable, Optional

if TYPE_CHECKING:
    from bokeh.plotting import figure
    from .ptplot import PTPlot


class Field(Layer):
    def __init__(
            self, vertical_orientation: bool = False,
            min_yardline: float = -13,
            max_yardline: float = 113,
            relative_yardlines: bool = False,
            sideline_buffer: float = 3,
            pixels_per_yard: int = 20):
        if vertical_orientation:
            raise NotImplementedError("Don't have that yet")

        self.vertical_orientation = vertical_orientation
        self.min_yardline = min_yardline
        self.max_yardline = max_yardline
        self.relative_yardlines = relative_yardlines
        self.sideline_buffer = sideline_buffer
        if pixels_per_yard < 10:
            warnings.warn("Using pixels_per_yard < 10 results in poor image quality an is not recommended")
        self.pixels_per_yard = pixels_per_yard

    def get_mappings(self):
        return []

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure):

        field_width_yards = 53.3
        y_min = 0 - self.sideline_buffer
        y_max = field_width_yards + self.sideline_buffer
        x_yards = self.max_yardline - self.min_yardline
        y_yards = y_max - y_min

        fig, ax = plt.subplots(
            figsize=(x_yards, y_yards), dpi=self.pixels_per_yard,
            tight_layout={"pad": 0}
        )
        ax.set_facecolor("green")
        ax.set_axis_off()
        ax.add_artist(ax.patch)
        ax.patch.set_zorder(-1)
        ax.set_xlim(self.min_yardline, self.max_yardline)
        ax.set_ylim(y_min, y_max)

        # Set up field lines
        yardlines = _get_vertical_line_locations(
            # If relative, just use max/min
            # If absolute, use max/min but not past the goal lines
            max(self.min_yardline, 0 if not self.relative_yardlines else self.min_yardline),
            min(self.max_yardline, 100 if not self.relative_yardlines else self.max_yardline),
            5
        )
        ax.vlines(yardlines, 0, field_width_yards, color="white", lw=20)
        if not self.relative_yardlines:
            endzone_yardlines = [
                yard
                for yard in [-10, 110]
                if yard > self.min_yardline and yard < self.max_yardline
            ]
            ax.vlines(endzone_yardlines, 0, field_width_yards, color="white", lw=40)

        if self.sideline_buffer > 0:
            ax.hlines(
                [0, field_width_yards], max(-10.2, self.min_yardline), min(110.2, self.max_yardline),
                color="white", lw=40
            )

        # Set up numbers
        number_yardlines = _get_vertical_line_locations(
            # If relative, just use max/min
            # If absolute, use max/min but not past the 10s
            max(self.min_yardline, 10 if not self.relative_yardlines else self.min_yardline),
            min(self.max_yardline, 90 if not self.relative_yardlines else self.max_yardline),
            10
        )

        number_options = {
            "fontsize": 150,
            "color": "white",
            "weight": "bold",
            "ha": "center",
            "va": "center"
        }
        for yardline in number_yardlines:
            number = yardline if self.relative_yardlines else 50 - abs(50 - yardline)
            string_marker = str(number)
            string_marker = (
                f" \u200a{string_marker}" if len(string_marker) == 1 else
                f"{string_marker[0]}\u200a{string_marker[1]}"
            )
            ax.text(yardline, 3, string_marker, **number_options)
            ax.text(yardline, 50, string_marker, **number_options, rotation=180)

        # Convert the plot to a numpy array, which can then be added to bokeh as a static image
        fig.canvas.draw()
        field = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        field = field.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close(fig)
        img = np.empty(field.shape[:2], dtype=np.uint32)
        field_view = img.view(dtype=np.uint8).reshape((field.shape[0], field.shape[1], 4))
        field_view[:, :, 0] = field[::-1, :, 0]
        field_view[:, :, 1] = field[::-1, :, 1]
        field_view[:, :, 2] = field[::-1, :, 2]
        field_view[:, :, 3] = 200

        bokeh_figure.image_rgba(image=[img], x=self.min_yardline, y=y_min, dw=x_yards, dh=y_yards)

        # Have to manually set the width here because I can't figure out how to make bokeh scale
        # to it automatically :(
        bokeh_figure.width = int(round(bokeh_figure.height * x_yards / y_yards))


def _get_vertical_line_locations(
        min_yards: float, max_yards: float, yard_modulus: int,
):
    vlines = [
        yard
        for yard in range(
            math.ceil(min_yards),
            math.floor(max_yards) + 1
        )
        if yard % yard_modulus == 0
    ]
    return vlines
