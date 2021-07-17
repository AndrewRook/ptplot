from __future__ import annotations

import math

import pandas as pd

from functools import partial

from ptplot.core import Layer, _Aesthetics, _Metadata
from typing import TYPE_CHECKING, Callable, Sequence

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
    return partial(figure.ellipse, width=2, height=1, angle=0.0, fill_color="brown", line_color="brown")


class Aesthetics(_Aesthetics):
    """
    Team colors and ball colors/marker for the NFL.
    """

    team_color_mapping = NFL_TEAMS
    ball_colors = ["brown", "brown"]
    ball_marker_generator = _ball_marker_generator


class Field(Layer):
    """Generate an NFL field.

    Parameters
    ----------
    min_yardline : The minimum yardline to use. Note that the default will cover the whole
        left/bottom endzone with a three-yard buffer.
    max_yardline : The maximum yardline to use. Note that the default will cover the whole
        right/top endzone with a three-yard buffer.
    relative_yardlines : If True, then the yardlines will be centered around zero rather than
        representing real positions on the field. This can be useful for plotting multiple
        plays on top of each other.
    sideline_buffer : How many yards of extra space to provide on each sideline.
    """

    def __init__(
        self,
        min_yardline: float = -13,
        max_yardline: float = 113,
        relative_yardlines: bool = False,
        sideline_buffer: float = 3,
    ):

        self.min_yardline = min_yardline
        self.max_yardline = max_yardline
        self.relative_yardlines = relative_yardlines
        self.sideline_buffer = sideline_buffer

    def get_mappings(self) -> Sequence[str]:
        return []

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata) -> None:

        field_width_yards = 53.3
        y_min = 0 - self.sideline_buffer
        y_max = field_width_yards + self.sideline_buffer
        x_yards = self.max_yardline - self.min_yardline
        y_yards = y_max - y_min

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

        # This is a total kludge to scale font size up and down with plot size,
        # based on a font size I found to work reasonably well
        pixels_per_data_unit = bokeh_figure.height / abs(bokeh_figure.y_range.end - bokeh_figure.y_range.start)
        font_size = pixels_per_data_unit * 3

        bokeh_figure.background_fill_color = "#34aa62"

        # Set up field lines
        yardlines = _get_vertical_line_locations(
            # If relative, just use max/min
            # If absolute, use max/min but not past the goal lines
            max(self.min_yardline, 0 if not self.relative_yardlines else self.min_yardline),
            min(self.max_yardline, 100 if not self.relative_yardlines else self.max_yardline),
            5,
        )
        bokeh_figure.rect(
            yardlines,
            [field_width_yards / 2] * len(yardlines),
            width=0.3,
            height=field_width_yards,
            fill_color="white",
            line_width=0,
            level="image",
        )
        if not self.relative_yardlines:
            endzone_yardlines = [yard for yard in [-10, 110] if yard > self.min_yardline and yard < self.max_yardline]
            bokeh_figure.rect(
                endzone_yardlines,
                [field_width_yards / 2] * len(endzone_yardlines),
                width=0.6,
                height=field_width_yards,
                fill_color="white",
                line_width=0,
                level="image",
            )
        if self.sideline_buffer > 0:
            lines_start = max(-10.2, self.min_yardline)
            lines_end = min(110.2, self.max_yardline)
            bokeh_figure.rect(
                [(lines_end + lines_start) / 2] * 2,
                [0, field_width_yards],
                height=0.6,
                width=lines_end - lines_start,
                fill_color="white",
                line_width=0,
                level="image",
            )

        # Set up numbers
        number_yardlines = _get_vertical_line_locations(
            # If relative, just use max/min
            # If absolute, use max/min but not past the 10s
            max(self.min_yardline, 10 if not self.relative_yardlines else self.min_yardline),
            min(self.max_yardline, 90 if not self.relative_yardlines else self.max_yardline),
            10,
        )
        string_markers = [
            str(yardline) if self.relative_yardlines else str(50 - abs(50 - yardline)) for yardline in number_yardlines
        ]
        string_markers = [
            f" \u0020\u2005{string_marker}"
            if len(string_marker) == 1
            else f"{string_marker[0]}\u2005{string_marker[1]}"
            for string_marker in string_markers
        ]
        bokeh_figure.text(
            number_yardlines,
            3,
            text=string_markers,
            text_align="center",
            text_baseline="middle",
            text_color="white",
            text_font_size=f"{font_size:.2f}px",
            level="image",
        )
        bokeh_figure.text(
            number_yardlines,
            50,
            text=string_markers,
            angle=math.pi,
            text_align="center",
            text_baseline="middle",
            text_color="white",
            text_font_size=f"{font_size:.2f}px",
            level="image",
        )

        return None


def _get_vertical_line_locations(
    min_yards: float,
    max_yards: float,
    yard_modulus: int,
) -> Sequence[int]:
    vlines = [yard for yard in range(math.ceil(min_yards), math.floor(max_yards) + 1) if yard % yard_modulus == 0]
    return vlines
