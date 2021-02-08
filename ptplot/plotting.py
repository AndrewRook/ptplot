import numpy as np
import pandas as pd
import plotly.graph_objects as go

from typing import Callable, Dict, Sequence, Union

from ._assets.core import Field
from ._assets.nfl_field import FIELD as NFL_FIELD
from ._assets.nfl_teams import TeamColors, TEAM_COLORS as NFL_TEAM_COLORS
from .utilities import _parse_none_callable_string

SPORT_FIELD_MAPPING = {"nfl": NFL_FIELD}


def animate_play(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    frame_column: str,
    hover_text: Union[None, str, Callable] = None,
    ball_identifier: Union[None, str, Callable] = None,
    home_away_identifier: Union[None, str, Callable] = None,
    team_abbreviations: Union[None, str, Callable] = None,
    uniform_number: Union[None, str, Callable] = None,
    fig=None,
    team_color_mapping: Dict[str, TeamColors] = NFL_TEAM_COLORS,
    slider_label_generator: Union[None, Callable] = None,
):
    """
    Animate a play.

    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    hover_text: Union[None, str, Callable] = None,
    ball_identifier: Union[None, str, Callable] = None,
    home_away_identifier: Union[None, str, Callable] = None,
    team_abbreviations: Union[None, str, Callable] = None,
    uniform_number: Union[None, str, Callable] = None,
    team_color_mapping: Dict[str, TeamColors] = NFL_TEAM_COLORS,
    fig: Union[None, go.Figure, Field, str] = None


    Parameters
    ----------
    frame_column
        The column name in ``data`` which has frame numbers in it
    slider_label_generator
        If ``None``, use the values in the ``frame_column`` to label the slider.
        If a function, apply the function to the ``data`` for each frame to generate
        slider labels. For example, the ``ptplot.utilities.generate_time_elapsed_labels``
        function.
    Other Fields
        See the documentation for ``ptplot.plotting.plot_frame``

    Returns
    -------
    plotly.graph_objects.Figure
        A Plotly Figure with player positions animated. If the user passes in a
        Figure, this will be the same Figure.

    Warnings
    --------
    This function assumes that the ordering of the players is the same in every
    frame. That is if the QB is the first row of frame 1, the QB is also the first
    row of frame 2+.

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
        hover_text=hover_text,
        ball_identifier=ball_identifier,
        home_away_identifier=home_away_identifier,
        team_abbreviations=team_abbreviations,
        uniform_number=uniform_number,
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


def create_field(figure: Union[go.Figure, None] = None, sport_field: Union[str, Field] = "nfl"):
    """
    Create the field markers used as a background to your plots.

    While it's possible to make plots with player tracking data against
    a regular white/gray background that your plotting package will use by
    default, it is much easier to interpret the plots when the data is plotted
    against a realistic representation of the playing field. This function automates
    the otherwise tedious creation of playing fields, and can then be used either
    as input to other functions in this library or for custom plots of your own.
    Parameters
    ----------
    figure
        If you have an existing plotly Figure object that you want to draw the
        field on top of, you can pass it in here. Otherwise, creates a new Figure object.
    sport_field
        What kind of field you would like. Defaults to a landscape-orientation NFL
        field. For options, see ``ptplot.plotting.SPORT_FIELD_MAPPING``. Additionally,
        instead of passing a string to map with ``SPORT_FIELD_MAPPING``, you can pass
        a ``ptplot._assets.core.Field`` object directly. This allows you to start with
        one of the premade fields and modify it to your liking (e.g. changing the field
        color or adding more padding around the fiel).

    Returns
    -------
    plotly.graph_objects.Figure
        A Plotly Figure with the field lines and markers drawn in. If the user passes in a
        Figure, this will be the same Figure.

    Notes
    -----
    The units of the field markers are in the physical units of the playing field. For example,
    the NFL fields will return a Figure with markers placed at the appropriate yardlines. If you
    pass in an input figure, make sure that any objects on it have matching units. Similarly,
    when using this field to plot data, make sure that your player tracking data has the same units.

    """
    if figure is None:
        figure = go.Figure()

    field_parameters = sport_field if type(sport_field) == Field else SPORT_FIELD_MAPPING[sport_field.lower()]

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


def lookup_team_colors(
    team_abbreviations: Sequence,
    lookup_table: Dict[str, TeamColors],
    num_colors_needed: int,
    team_is_home_flags: Union[Sequence, None] = None,
    null_team_colors: Sequence = ["black", "black", "black"],
):
    """Map team color information to an iterable of team identifiers.

    This function is primarily intended for use by other functions in this library,
    but is exposed to users in case it is helpful for making custom plots not currently
    supported by this library.

    Parameters
    ----------
    team_abbreviations
        An iterable of abbreviations (likely strings) of team names. For example, "CLE"
        for the Cleveland Browns.
    lookup_table
        A dictionary which maps the abbreviations to team color schemes, with each color
        scheme represented by a helper class called ``TeamColors``. Generally users should
        not be creating this table themselves: instead find the scheme you need in
        ``ptplot._assets`` (for example, NFL team colors are in
        ``ptplot._assets.nfl_teams.TEAM_COLORS``).
    num_colors_needed
        How many colors you need. For example, if you just want to make a scatterplot of
        some aggregated player tracking data and you want to color each point by team color,
        you might only need one color. Alternatively, for animating a single play you may want
        three colors: one for the marker itself, one for the edge of the marker, and one for the
        player's number.
    team_is_home_flags
        An optional boolean flag where True means the team is the home team. If this flag is set,
        the function will pull the appropriate home/away colors for each team. If this flag is
        not set, home colors will be pulled for everyone.
    null_team_colors
        The colors to use if a team abbreviation is null. This often happens when the ball is
        included in the list of identifiers.

    Returns
    -------
    A list of ``num_colors_needed`` tuples, where the first tuple is the primary color for
    each element of the ``team_abbreviations`` iterable, the second tuple is the
    secondary color, etc.

    Warnings
    --------
    This function is unoptimized, and is designed for use on small datasets only.
    """
    colors_list = []
    # If no flags are passed, make everyone the home team
    team_is_home_flags = (
        np.ones(len(team_abbreviations), dtype=bool) if team_is_home_flags is None else team_is_home_flags
    )
    for abbreviation, is_home_flag in zip(team_abbreviations, team_is_home_flags):
        if pd.isnull(abbreviation):
            team_colors = null_team_colors
        elif is_home_flag == True:  # noqa: E712
            team_colors = lookup_table[abbreviation].home
        else:
            team_colors = lookup_table[abbreviation].away

        colors_list.append([team_colors[j] for j in range(num_colors_needed)])

    return list(zip(*colors_list))


def plot_frame(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    hover_text: Union[None, str, Callable] = None,
    ball_identifier: Union[None, str, Callable] = None,
    home_away_identifier: Union[None, str, Callable] = None,
    team_abbreviations: Union[None, str, Callable] = None,
    uniform_number: Union[None, str, Callable] = None,
    team_color_mapping: Dict[str, TeamColors] = NFL_TEAM_COLORS,
    fig: Union[None, go.Figure, Field, str] = None,
):
    """

    Parameters
    ----------
    data
        The data for the given frame.
    x_column
        The column name of the column in ``data`` that contains x-axis values
    y_column
        The column name of the column in ``data`` that contains y-axis values
    hover_text
        Either ``None`` for no special hover text (will still show x/y coordinates),
        a function which takes in `data` and returns an array of string labels, or a string
        indicating a column of ``data`` that contains the labels.
        For example, the output of the ``ptplot.utilities.generate_labels_from_columns``
        function.
    ball_identifier
        Either ``None`` for no special marker for the ball, a function which takes in
        `data` and returns a boolean array where ``True`` indicates a row with data
        for the ball, or a string indicating the column of ``data`` with those booleans.
        For example, ``lambda data: data["displayName"] == "Football"``.
        Also, see note below about available ball markers.
    home_away_identifier
        Either ``None`` for no home/away color-coding, a function which takes in ``data`` and
        returns a boolean array where ``True`` indicates a row with the home team and ``False``
        is a row with the away team, or a string indicating the column of ``data`` with those
        booleans. For example, ``lambda data: data["team"] == "home"``.
        If ``ball_identifier`` is set, whatever value assigned to the
        ball will override the value assigned by this function.
    team_abbreviations
        Either ``None`` to not color-code players by team, a function which takes in ``data`` and
        returns a string array of team abbreviations, or a string indicating the column of
        ``data`` that contains the abbreviations.
    uniform_number
        Either ``None`` to not put uniform numbers on markers, a function which takes in ``data``
        and returns an array of the uniform numbers, or a string indicating the column of ``data``
        that contains the numbers.
    team_color_mapping
        A dictionary mapping team abbreviations to team colors. Defaults to NFL teams.
    fig
        If an instance of ``plotly.graph_objects.Figure``,
        plot on top of that figure. Otherwise corresponds to the ``sport_field`` keyword argument
        of ``ptplot.plotting.create_field``.

    Returns
    -------
    plotly.graph_objects.Figure
        A Plotly Figure with player positions marked. If the user passes in a
        Figure, this will be the same Figure.

    Notes
    -----
    At this time, the only ball marker that is supported is a brown diamond, which roughly
    approximates an American football. If you would like to use a different ball marker
    please put in a feature request (or better yet, a pull request implementing this).

    """
    # First, parse out all of the optional arguments:
    hover_text = _parse_none_callable_string(hover_text, data, "")
    is_ball = _parse_none_callable_string(ball_identifier, data, False)
    mode = "markers" if uniform_number is None else "markers+text"
    text = _parse_none_callable_string(uniform_number, data, None)

    team_abbreviations = (
        # A little different because abbreviations are all-or-nothing
        team_abbreviations
        if team_abbreviations is None
        else _parse_none_callable_string(team_abbreviations, data, "NA")
    )
    home_away_flag = _parse_none_callable_string(home_away_identifier, data, True)

    (
        marker_color,
        marker_edge_color,
        marker_textfont_color,
        marker_width,
        marker_size,
        marker_symbol,
    ) = _get_style_information(data, home_away_flag, team_abbreviations, team_color_mapping)

    marker_color[is_ball] = "brown"
    marker_edge_color[is_ball] = "black"
    marker_symbol[is_ball] = "diamond-wide"
    marker_width[is_ball] = 1
    marker_size[is_ball] = 12

    if fig is None:
        fig = create_field()
    elif type(fig) in [str, Field]:
        fig = create_field(sport_field=fig)

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
        color_tuples = lookup_team_colors(team_abbreviations, abbreviation_lookup_table, 3, team_is_home_flags=is_home)
        marker_colors = pd.DataFrame(
            {
                colname: color
                for colname, color in zip(["marker_color", "marker_edge_color", "marker_textfont_color"], color_tuples)
            }
        )
    else:
        marker_colors = pd.DataFrame(
            {
                "marker_color": np.where(is_home == 0, away_marker_color, home_marker_color),
                "marker_edge_color": np.where(is_home == 0, away_marker_edge_color, home_marker_edge_color),
                "marker_textfont_color": np.where(is_home == 0, away_marker_textfont_color, home_marker_textfont_color),
            }
        )
    return (
        marker_colors["marker_color"].values,
        marker_colors["marker_edge_color"].values,
        marker_colors["marker_textfont_color"].values,
    )


def _get_style_information(
    data: pd.DataFrame,
    is_home: np.array,
    team_column: Union[None, np.array],
    team_color_mapping: Dict[str, TeamColors],
):
    """
    Warning
    -------
    Team color mapping is unoptimized and should not be used on large datasets
    """

    # Marker styling
    marker_color, marker_edge_color, marker_textfont_color = _generate_markers(is_home, team_column, team_color_mapping)
    marker_width = np.tile([2], len(data))
    marker_size = np.tile([16], len(data))
    marker_symbol = np.tile(np.array(["circle"], dtype="U40"), len(data))
    return marker_color, marker_edge_color, marker_textfont_color, marker_width, marker_size, marker_symbol


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
