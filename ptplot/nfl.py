from __future__ import annotations

import math
import matplotlib

import numpy as np
import pandas as pd
import warnings

from functools import partial

from ptplot.core import Layer, _Aesthetics, _Metadata
from typing import TYPE_CHECKING, Callable, Sequence

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

if TYPE_CHECKING:
    from bokeh.models import GlyphRenderer
    from bokeh.plotting import figure
    from .ptplot import PTPlot


NFL_TEAMS = {
    "ARI": ("#97233f", "white"),
    "ATL": ("#a71930", "#a5acaf"),
    "BAL": ("#241773", "#9e7c0c"),
    "BUF": ("#00338d", "#c60c30"),
    "CAR": ("#0085ca", "#bfc0bf"),
    "CHI": ("#0b162a", "#c83803"),
    "CIN": ("#fb4f14", "white"),
    "CLE": ("#311d00", "#ff3c00"),
    "DAL": ("#002244", "#869397"),
    "DEN": ("#fb4f14", "#002244"),
    "DET": ("#0076b6", "#b0b7bc"),
    "GB": ("#203731", "#ffb612"),
    "HOU": ("#03202f", "#a71930"),
    "IND": ("#002c5f", "#a5acaf"),
    "JAX": ("#006778", "#9f792c"),
    "KC": ("#e31837", "#ffb612"),
    "LAC": ("#0073cf", "#ffb612"),
    "LAR": ("#002244", "#b3995d"),
    "LV": ("black", "#a5acaf"),
    "MIA": ("#008e97", "#f26a24"),
    "MIN": ("#4f2683", "#ffc62f"),
    "NE": ("#002244", "#c60c30"),
    "NO": ("black", "#d3bc8d"),
    "NYG": ("#0b2265", "#a71930"),
    "NYJ": ("#003f2d", "white"),
    "PHI": ("#004c54", "#a5acaf"),
    "PIT": ("black", "#ffb612"),
    "SF": ("#aa0000", "#b3995d"),
    "SEA": ("#002244", "#69be28"),
    "TB": ("#d50a0a", "#34302b"),
    "TEN": ("#002244", "#4b92db"),
    "WAS": ("#773141", "#ffb612"),
    "OAK": ("black", "#a5acaf"),
    "STL": ("#002244", "#b3995d"),
}


def _ball_marker_generator(figure: figure) -> Callable[[figure], Callable[..., GlyphRenderer]]:
    return partial(
        figure.ellipse, width=2, height=1, angle=0.0,
        fill_color="brown", fill_alpha=0.9, line_color="brown"
    )


class Aesthetics(_Aesthetics):
    """
    Team colors and ball colors/marker for the NFL.
    """
    team_color_mapping = NFL_TEAMS
    ball_colors = ["brown", "brown"]
    ball_marker_generator = _ball_marker_generator


class Field(Layer):
    """Generate an NFL field.

    The field is created by first making a pixel image with matplotlib, then loading
    the rgba array into Bokeh. This is less-than-ideal but was the easiest way to make
    the numerals that need to be on the field in such a way that they appropriately zoom.

    Parameters
    ----------
    vertical_orientation : If True, the long axis of the field will be the y-axis.
    min_yardline : The minimum yardline to use. Note that the default will cover the whole
        left/bottom endzone with a three-yard buffer.
    max_yardline : The maximum yardline to use. Note that the default will cover the whole
        right/top endzone with a three-yard buffer.
    relative_yardlines : If True, then the yardlines will be centered around zero rather than
        representing real positions on the field. This can be useful for plotting multiple
        plays on top of each other.
    sideline_buffer : How many yards of extra space to provide on each sideline.
    pixels_per_yard : The resolution of the image to generate. Larger numbers are higher resolution,
        but may lead to larger file sizes and longer load times.
    """
    def __init__(
        self,
        vertical_orientation: bool = False,
        min_yardline: float = -13,
        max_yardline: float = 113,
        relative_yardlines: bool = False,
        sideline_buffer: float = 3,
        pixels_per_yard: int = 20,
    ):
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

    def get_mappings(self) -> Sequence[str]:
        return []

    def draw(
            self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata
    ) -> None:

        field_width_yards = 53.3
        y_min = 0 - self.sideline_buffer
        y_max = field_width_yards + self.sideline_buffer
        x_yards = self.max_yardline - self.min_yardline
        y_yards = y_max - y_min

        fig, ax = plt.subplots(figsize=(x_yards, y_yards), dpi=self.pixels_per_yard, tight_layout={"pad": 0})
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
            5,
        )
        ax.vlines(yardlines, 0, field_width_yards, color="white", lw=20)
        if not self.relative_yardlines:
            endzone_yardlines = [yard for yard in [-10, 110] if yard > self.min_yardline and yard < self.max_yardline]
            ax.vlines(endzone_yardlines, 0, field_width_yards, color="white", lw=40)

        if self.sideline_buffer > 0:
            ax.hlines(
                [0, field_width_yards],
                max(-10.2, self.min_yardline),
                min(110.2, self.max_yardline),
                color="white",
                lw=40,
            )

        # Set up numbers
        number_yardlines = _get_vertical_line_locations(
            # If relative, just use max/min
            # If absolute, use max/min but not past the 10s
            max(self.min_yardline, 10 if not self.relative_yardlines else self.min_yardline),
            min(self.max_yardline, 90 if not self.relative_yardlines else self.max_yardline),
            10,
        )

        number_options = {"fontsize": 150, "color": "white", "weight": "bold", "ha": "center", "va": "center"}
        for yardline in number_yardlines:
            number = yardline if self.relative_yardlines else 50 - abs(50 - yardline)
            string_marker = str(number)
            string_marker = (
                f" \u200a{string_marker}" if len(string_marker) == 1 else f"{string_marker[0]}\u200a{string_marker[1]}"
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

        bokeh_figure.image_rgba(image=[img], x=self.min_yardline, y=y_min, dw=x_yards, dh=y_yards, level="image")

        # Have to manually set the width here because I can't figure out how to make bokeh scale
        # to it automatically :(
        bokeh_figure.width = int(round(bokeh_figure.height * x_yards / y_yards))

        # For some reason you have to manually specify the range bounds here in order to be able
        # access them downstream (apparently otherwise they're only computed in the JS, see
        # https://stackoverflow.com/a/50735228/1373664
        bokeh_figure.x_range.start = self.min_yardline
        bokeh_figure.x_range.end = self.max_yardline
        bokeh_figure.y_range.start = y_min
        bokeh_figure.y_range.end = y_max

        return None


def _get_vertical_line_locations(
    min_yards: float,
    max_yards: float,
    yard_modulus: int,
) -> Sequence[int]:
    vlines = [yard for yard in range(math.ceil(min_yards), math.floor(max_yards) + 1) if yard % yard_modulus == 0]
    return vlines
