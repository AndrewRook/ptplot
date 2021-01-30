import numpy as np
import pandas as pd
import plotly.graph_objects as go

from typing import Callable, Dict, Union, Sequence

from ._assets import nfl_field as field
from ._assets.nfl_teams import TeamColors, TEAM_COLORS

def get_path_midpoint(path):
    min_x, max_x, min_y, max_y = path.bbox()
    midpoint_x = (max_x + min_x) / 2
    midpoint_y = (max_y + min_y) / 2
    return complex(midpoint_x, midpoint_y)


def make_vline(y0, y1, x, **kwargs):
    """Make a vertical line of a defined distance."""
    return dict(
        type="line",
        y0=y0, y1=y1,
        x0=x, x1=x,
        **kwargs
    )


def make_hline(x0, x1, y, **kwargs):
    """Make a horizontal line of a defined distance."""
    return dict(
        type="line",
        y0=y, y1=y,
        x0=x0, x1=x1,
        **kwargs
    )


def create_field(figure=None):
    if figure is None:
        figure = go.Figure()

    # All units are in yards
    field_length = 120
    field_width = 53.3
    # First, make the field border:
    field_kwargs = {"line_width": 5, "line_color": "white", "layer": "below"}
    field_border = [
        make_hline(0, field_length, 0, **field_kwargs),
        make_hline(0, field_length, field_width, **field_kwargs),
        make_vline(0, field_width, 0, **field_kwargs),
        make_vline(0, field_width, field_length, **field_kwargs)
    ]

    # Now make the yard and hash lines:
    line_kwargs = {"line_width": 2, "line_color": "white", "layer": "below"}
    five_yard_lines = [
        make_vline(0, field_width, 5 * i, **line_kwargs)
        for i in range(2, 23)
    ]
    hash_width = 2 / 3 # Hashes are 2/3rds of a yard
    hash_length = 6 + 6/36 # six yards, six inches
    one_yard_lines = [
        make_vline(w, w + hash_width, i, **line_kwargs)
        for i in range(10, 111)
        if i % 10 != 0
        for w in [1, 23.58333, 23.58333 + hash_length - hash_width, 52.3 - hash_width]
    ]

    field_lines = field_border + five_yard_lines + one_yard_lines

    number_kwargs = {"line_color": "white", "fillcolor": "white", "layer": "below"}
    number_x_location_mapping = {
        20: field.ONE,
        30: field.TWO,
        40: field.THREE,
        50: field.FOUR,
        60: field.FIVE,
        70: field.FOUR,
        80: field.THREE,
        90: field.TWO,
        100: field.ONE
    }
    field_numbers = [
        [
            dict(type="path", path=value.translated(key - 2.7 + 4j).d(), **number_kwargs),
            dict(type="path", path=field.ZERO.translated(key + 0.5 + 4j).d(), **number_kwargs),
            dict(type="path", path=field.ZERO.translated(key - 3 + 47j).d(), **number_kwargs),
            dict(
                type="path",
                path=value.rotated(180, get_path_midpoint(value)).translated(key + 0.5 + 47j).d(),
                **number_kwargs
            )
        ]
        for key, value in number_x_location_mapping.items()
    ]
    # Flatten
    field_numbers = sum(field_numbers, [])

    # Numbers and arrows
    field_indicators = [
        [
            dict(
                type="path",
                path=f"M {xval - 3.2} 5.2 L {xval - 3.7} 5.45 L {xval - 3.2} 5.7 L {xval - 3.2} 5.2 Z",
                **number_kwargs
            ),
            dict(
                type="path",
                path=f"M {120 - xval + 3.6} 5.2 L {120 -xval + 4.1} 5.45 L {120 - xval + 3.6} 5.7 L {120 - xval + 3.6} 5.2 Z",
                **number_kwargs
            ),
            dict(
                type="path",
                path=f"M {xval - 3.6} 48.5 L {xval - 4.1} 48.25 L {xval - 3.6} 48.0 L {xval - 3.6} 48.5 Z",
                **number_kwargs
            ),
            dict(
                type="path",
                path=f"M {120 - xval + 3.2} 48.5 L {120 - xval + 3.7} 48.25 L {120 - xval + 3.2} 48.0 L {120 - xval + 3.2} 48.5 Z",
                **number_kwargs
            )
        ]
        for xval in [20, 30, 40, 50]
    ]
    # Flatten
    field_indicators = sum(field_indicators, [])

    figure.update_layout(
        xaxis_showgrid=False, yaxis_showgrid=False,  # remove grid lines
        xaxis_zeroline=False, yaxis_zeroline=False,  # remove axis lines
        plot_bgcolor="rgb(62, 126, 0)",  # set the background color
        yaxis_range=[-5, field_width + 5], xaxis_range=[-3, field_length + 3],  # set the range with a 2-yard buffer on each side
        shapes=field_lines + field_numbers + field_indicators
    )
    figure.update_xaxes(showticklabels=False)
    figure.update_yaxes(showticklabels=False)

    return figure


def plot_frame(
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        hover_text: Callable = None,
        ball_identifier: Callable = None,
        home_away_column: str = None,
        team_column: str = None,
        uniform_number_column: str = None,
        fig=None
):

    # First, set some defaults for the marker styling. We expect
    # most of these to get overriden via the optional kwargs
    marker_color = pd.Series(["gainsboro"] * len(data))
    marker_edge_color = pd.Series(["darkslategray"] * len(data))
    marker_symbol = pd.Series(["circle"] * len(data))
    marker_width = pd.Series([2] * len(data))
    marker_size = pd.Series([16] * len(data))

    if uniform_number_column is None:
        mode = "markers"
        text = None
    else:
        mode = "markers+text"
        text = data[uniform_number_column]
        textfont_color = pd.Series(["black"] * len(data))

    if home_away_column is not None and team_column is None:
        is_home_team = (data[home_away_column].str.lower() == "home").values
        marker_color[is_home_team] = "darkslategray"
        marker_edge_color[is_home_team] = "gainsboro"
        textfont_color[is_home_team] = "white"
    elif team_column is not None and home_away_column is None:
        # marker
        # for team_abbreviation in data[team_column]:
        raise NotImplementedError
    elif team_column is not None and home_away_column is not None:
        raise NotImplementedError

    hovertext = ""
    if hover_text is not None:
        hovertext = hover_text(data)

    if team_column is not None:
        raise NotImplementedError

    if ball_identifier is not None:
        is_ball = ball_identifier(data)
    else:
        is_ball = np.array([False] * len(data))

    marker_color[is_ball] = "brown"
    marker_edge_color[is_ball] = "black"
    marker_symbol[is_ball] = "diamond-wide"
    marker_width[is_ball] = 1
    marker_size[is_ball] = 12

    if fig is None:
        fig = create_field()

    fig.add_trace(go.Scatter(
        x=data[x_column], y=data[y_column], mode=mode,
        hovertext=hovertext,
        text=text, textfont_size=9, textfont_family=["Gravitas One"], textfont_color=textfont_color,
        marker={
            "size": marker_size, "color": marker_color, "symbol": marker_symbol, "opacity": 1,
            "line": {"width": marker_width, "color": marker_edge_color}
        }
    ))
    return fig


def lookup_team_colors(
        team_abbreviations: Sequence,
        lookup_table: Dict[str, TeamColors],
        num_colors_needed: int,
        team_is_home_flag: Sequence = None
):
    """Map team color information to an iterable of team identifiers.

    ``team_is_home_flag`` is an optional boolean flag where True means the
    team is the home team. If this flag is set, the function will pull the
    appropriate home/away colors for each team.

    Returns
    -------
    ``num_colors_needed`` lists, where the first list is the primary color for
    each element of the ``team_abbreviations`` list, the second list is the
    secondary color, etc.

    Warnings
    --------
    This function is unoptimized, and is designed for use on small datasets only.
    """
    colors_list = []
    for i, abbreviation in team_abbreviations:
        if team_is_home_flag is None or team_is_home_flag[i] is True:
            team_colors = lookup_table[abbreviation].home
        else:
            team_colors = lookup_table[abbreviation].away

        colors_list.append([
            team_colors[j]
            for j in range(num_colors_needed)
        ])

    return list(zip(*colors_list))
