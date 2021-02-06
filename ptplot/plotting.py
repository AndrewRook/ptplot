import numpy as np
import pandas as pd
import plotly.graph_objects as go

from typing import Callable, Dict, Sequence, Union

from ._assets.nfl_field import FIELD as NFL_FIELD
from ._assets.nfl_teams import TeamColors, TEAM_COLORS as NFL_TEAM_COLORS

SPORT_FIELD_MAPPING = {"nfl": NFL_FIELD}


def create_field(figure=None, sport="nfl"):
    if figure is None:
        figure = go.Figure()

    field_parameters = SPORT_FIELD_MAPPING[sport.lower()]

    figure.update_layout(
        xaxis_showgrid=False,
        yaxis_showgrid=False,  # remove grid lines
        xaxis_zeroline=False,
        yaxis_zeroline=False,  # remove axis lines
        plot_bgcolor=field_parameters.background_color,  # set the background color
        yaxis_range=[-field_parameters.width_padding, field_parameters.width + field_parameters.width_padding],
        xaxis_range=[-field_parameters.length_padding, field_parameters.length + field_parameters.length_padding],
        shapes=field_parameters.lines_markers,
    )
    figure.update_xaxes(showticklabels=False)
    figure.update_yaxes(showticklabels=False)

    return figure


def get_style_information(
    data: pd.DataFrame,
    home_identifier: Union[None, Callable],
    team_column: Union[None, str],
    team_color_mapping: Dict[str, TeamColors],
):
    """
    Warning
    -------
    Team color mapping is unoptimized and should not be used on large datasets
    """
    is_home = np.tile([-1], len(data)) if not home_identifier else home_identifier(data)
    team_column = None if team_column is None else data[team_column]

    # Marker styling
    marker_color, marker_edge_color, marker_textfont_color = _generate_markers(is_home, team_column, team_color_mapping)
    marker_width = np.tile([2], len(data))
    marker_size = np.tile([16], len(data))
    marker_symbol = np.tile(np.array(["circle"], dtype="U40"), len(data))
    return marker_color, marker_edge_color, marker_textfont_color, marker_width, marker_size, marker_symbol


def _generate_markers(
    is_home: np.array,
    team_abbreviations: Union[pd.Series, None],
    abbreviation_lookup_table: Dict[str, TeamColors] = NFL_TEAM_COLORS,
):
    # Set defaults:
    home_marker_color = np.tile(np.array(["gainsboro"], dtype="U40"), len(is_home))
    home_marker_edge_color = np.tile(np.array(["darkslategray"], dtype="U40"), len(is_home))
    home_marker_textfont_color = np.tile(np.array(["black"], dtype="U40"), len(is_home))

    away_marker_color = np.tile(np.array(["darkslategray"], dtype="U40"), len(is_home))
    away_marker_edge_color = np.tile(np.array(["gainsboro"], dtype="U40"), len(is_home))
    away_marker_textfont_color = np.tile(np.array(["white"], dtype="U40"), len(is_home))

    if team_abbreviations is not None:
        for i, abbreviation in enumerate(team_abbreviations):
            if pd.isnull(abbreviation):
                continue
            home_colors = abbreviation_lookup_table[abbreviation].home
            away_colors = abbreviation_lookup_table[abbreviation].away

            home_marker_color[i] = home_colors[0]
            home_marker_edge_color[i] = home_colors[1]
            home_marker_textfont_color[i] = home_colors[2]

            away_marker_color[i] = away_colors[0]
            away_marker_edge_color[i] = away_colors[1]
            away_marker_textfont_color[i] = away_colors[2]

    marker_color = np.where(is_home == 0, away_marker_color, home_marker_color)
    marker_edge_color = np.where(is_home == 0, away_marker_edge_color, home_marker_edge_color)
    marker_textfont_color = np.where(is_home == 0, away_marker_textfont_color, home_marker_textfont_color)
    return marker_color, marker_edge_color, marker_textfont_color


def plot_frame(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    hover_text_generator: Union[None, Callable] = None,
    ball_identifier: Union[None, Callable] = None,
    home_away_identifier: Union[None, Callable] = None,
    team_column: str = None,
    uniform_number_column: str = None,
    fig=None,
    team_color_mapping: Dict[str, TeamColors] = NFL_TEAM_COLORS,
):
    (
        marker_color,
        marker_edge_color,
        marker_textfont_color,
        marker_width,
        marker_size,
        marker_symbol,
    ) = get_style_information(data, home_away_identifier, team_column, team_color_mapping)

    if uniform_number_column is None:
        mode = "markers"
        text = None
    else:
        mode = "markers+text"
        text = data[uniform_number_column]

    hover_text = "" if not hover_text_generator else hover_text_generator(data)

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

    fig.add_trace(
        go.Scatter(
            x=data[x_column],
            y=data[y_column],
            mode=mode,
            hovertext=hover_text,
            text=text,
            textfont_size=9,
            textfont_family=["Gravitas One"],
            textfont_color=marker_textfont_color,
            marker={
                "size": marker_size,
                "color": marker_color,
                "symbol": marker_symbol,
                "opacity": 1,
                "line": {"width": marker_width, "color": marker_edge_color},
            },
        )
    )
    return fig


def animate_play(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    frame_column: str,
    hover_text_generator: Union[None, Callable] = None,
    ball_identifier: Union[None, Callable] = None,
    home_away_identifier: Union[None, Callable] = None,
    team_column: str = None,
    uniform_number_column: str = None,
    fig=None,
    team_color_mapping: Dict[str, TeamColors] = NFL_TEAM_COLORS,
    slider_label_generator: Union[None, Callable] = None,
):
    """
    Animate a play.

    .. Warning::
        This function assumes that the ordering of the players is the same in every
        frame. That is if the QB is the first row of frame 1, the QB is also the first
        row of frame 2+.

    Parameters
    ----------
    data
    x_column
    y_column
    frame_column
    hover_text_generator
    ball_identifier
    home_away_identifier
    team_column
    uniform_number_column
    fig
    team_color_mapping
    slider_label_generator

    Returns
    -------

    """
    frame_groups = data.groupby(frame_column)
    slider_labels = [
        frame_number if slider_label_generator is None else slider_label_generator(frame_data)
        for frame_number, frame_data in frame_groups
    ]
    # This abuses the fact that groupby sorts the grouping column
    # in ascending order by default
    first_frame = frame_groups.get_group(data[frame_column].min())

    # Use the first frame to set up all the marker stylings
    fig = plot_frame(
        first_frame,
        x_column,
        y_column,
        hover_text_generator=hover_text_generator,
        ball_identifier=ball_identifier,
        home_away_identifier=home_away_identifier,
        team_column=team_column,
        uniform_number_column=uniform_number_column,
        fig=fig,
        team_color_mapping=team_color_mapping,
    )

    # Make the animation frames
    frame_plots = []
    for frame_id, frame_data in frame_groups:
        frame_plots.append(
            go.Frame(data=[go.Scatter(x=frame_data[x_column], y=frame_data[y_column])], name=str(frame_id))
        )
    fig.frames = frame_plots

    # Add animation controls
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                yanchor="bottom",
                xanchor="left",
                x=0.05,
                y=-0.17,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 100, "redraw": False},
                                "fromcurrent": True,
                            },
                        ],
                    ),
                    {
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                        "label": "Pause",
                        "method": "animate",
                    },
                ],
            )
        ],
        sliders=_make_sliders([frame.name for frame in fig.frames], slider_labels),
    )
    return fig


def _make_sliders(frame_names: Sequence, slider_labels: Sequence, **slider_kwargs):
    if len(frame_names) != len(slider_labels):
        raise IndexError("Frame names and slider labels must have same length")
    if "steps" in slider_kwargs:
        raise NotImplementedError("Cannot overwrite arguments in the slider steps")
    slider_steps = [
        {
            "args": [
                [frame_name],
                {
                    "frame": {"duration": 100},
                    "mode": "immediate",
                    "fromcurrent": True,
                    "transition": {"duration": 100, "easing": "cubic-out"},
                },
            ],
            "label": slider_labels[i],
            "method": "animate",
        }
        for i, frame_name in enumerate(frame_names)
    ]

    slider_kwargs["len"] = slider_kwargs.get("len", 0.7)
    slider_kwargs["x"] = slider_kwargs.get("x", 0.2)
    slider_kwargs["y"] = slider_kwargs.get("y", 0.05)

    sliders = [{**slider_kwargs, "steps": slider_steps}]

    return sliders


def lookup_team_colors(
    team_abbreviations: Sequence,
    lookup_table: Dict[str, TeamColors],
    num_colors_needed: int,
    team_is_home_flag: Sequence = None,
):
    """Map team color information to an iterable of team identifiers.

    ``team_is_home_flag`` is an optional boolean flag where True means the
    team is the home team. If this flag is set, the function will pull the
    appropriate home/away colors for each team.

    Returns
    -------
    ``num_colors_needed`` tuples, where the first tuple is the primary color for
    each element of the ``team_abbreviations`` iterable, the second tuple is the
    secondary color, etc.

    Warnings
    --------
    This function is unoptimized, and is designed for use on small datasets only.
    """
    colors_list = []
    for i, abbreviation in enumerate(team_abbreviations):
        if team_is_home_flag is None or team_is_home_flag[i] == True:
            team_colors = lookup_table[abbreviation].home
        else:
            team_colors = lookup_table[abbreviation].away

        colors_list.append([team_colors[j] for j in range(num_colors_needed)])

    return list(zip(*colors_list))
