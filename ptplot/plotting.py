import numpy as np
import pandas as pd
import plotly.graph_objects as go

from typing import Callable, Sequence, Union

from ._assets.core import Field
from ._assets.nfl_field import FIELD as NFL_FIELD, VERTICAL_FIELD as VERTICAL_NFL_FIELD
from ._assets.nfl_teams import TEAM_COLORS as NFL_TEAM_COLORS
from .utilities import _parse_none_callable_string

SPORT_FIELD_MAPPING = {"nfl": NFL_FIELD, "nfl_vertical": VERTICAL_NFL_FIELD}


def animate_positions(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    frame_column: str,
    seconds_per_frame: float = 0.1,
    hover_text: Union[None, str, Callable] = None,
    ball_identifier: Union[None, str, Callable] = None,
    home_away_identifier: Union[None, str, Callable] = None,
    team_abbreviations: Union[None, str, Callable] = None,
    uniform_number: Union[None, str, Callable] = None,
    fig=None,
    team_color_mapping: pd.DataFrame = NFL_TEAM_COLORS,
    slider_label_generator: Union[None, Callable] = None,
    events_of_interest: Union[None, str, Callable] = None,
):
    """
    Animate a play. Player and ball positions are represented by moving
    markers. The animation generates play and pause buttons, plus a slider
    that can be moved to skip to a specific frame.


    Parameters
    ----------
    frame_column
        The column name in ``data`` which has frame numbers in it
    seconds_per_frame
        How many seconds there are between frames.
    slider_label_generator
        If ``None``, use the values in the ``frame_column`` to label the slider.
        If a function, apply the function to the ``data`` for each frame to generate
        slider labels. For example, the ``ptplot.utilities.generate_time_elapsed_labels``
        function.
    events_of_interest
        If not ``None``, add a dropdown to move the animation tagged as an event. If
        a function, takes in the data for a frame and returns a string with the name of
        the event in that frame or a null value. If a string, the column in the input
        data that is non-null when a frame has an event in it.
    Other fields
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
    fig = plot_positions(
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
    event_mapping = []
    for frame_id, frame_data in frame_groups:
        frame_plots.append(
            go.Frame(data=[go.Scatter(x=frame_data[x_column], y=frame_data[y_column])], name=str(frame_id))
        )
        # TODO: refactor this with utilities._parse_none_callable_string, if possible
        if events_of_interest is not None:
            if len(event_mapping) == 0:
                event_mapping.append((frame_id, "Reset"))
                continue
            try:
                event_in_frame = events_of_interest(frame_data)
            except TypeError:
                event_in_frame = frame_data[events_of_interest]
            unique_events_in_frame = pd.unique(event_in_frame)
            if len(unique_events_in_frame) != 1:
                raise KeyError(f"Multiple events in frame {frame_id}. Got {unique_events_in_frame}")
            if pd.isnull(unique_events_in_frame[0]) is False and unique_events_in_frame[0].lower() != "none":
                event_mapping.append((frame_id, unique_events_in_frame[0]))
    fig.frames = _safe_add_frames(fig, frame_plots)

    # Add animation controls
    reset_name = fig.frames[0].name if events_of_interest is None else None
    buttons = _make_control_buttons(seconds_per_frame * 1000, reset_name)
    events = None if events_of_interest is None else _make_event_dropdown(event_mapping)

    fig.update_layout(
        updatemenus=[buttons] if events is None else [buttons, events],
        sliders=_make_sliders([frame.name for frame in fig.frames], slider_labels),
    )
    return fig


def animate_tracks(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    player_column: str,
    frame_column: str,
    seconds_per_frame: float = 0.1,
    hover_text: Union[None, str, Callable] = None,
    ball_identifier: Union[None, str, Callable] = None,
    home_away_identifier: Union[None, str, Callable] = None,
    team_abbreviations: Union[None, str, Callable] = None,
    team_color_mapping: pd.DataFrame = NFL_TEAM_COLORS,
    fig: Union[None, go.Figure, Field, str] = None,
    slider_label_generator: Union[None, Callable] = None,
    events_of_interest: Union[None, str, Callable] = None,
):

    first_frame = data[frame_column].min()

    fig = plot_tracks(
        data[data[frame_column] == first_frame],
        x_column,
        y_column,
        player_column,
        hover_text=hover_text,
        ball_identifier=ball_identifier,
        home_away_identifier=home_away_identifier,
        team_abbreviations=team_abbreviations,
        team_color_mapping=team_color_mapping,
        fig=fig,
    )

    # Make the animation frames
    frame_plots = []
    slider_labels = []
    event_mapping = []
    for frame_id in data[frame_column].unique():
        frame_data = data[data[frame_column] <= frame_id]

        player_groups = frame_data.groupby(player_column)
        frame_tracks = []
        for player_name, player_data in player_groups:
            frame_tracks.append(
                go.Scatter(
                    x=player_data[x_column],
                    y=player_data[y_column],
                    # Need to re-parse the text because the number of points changes :(
                    text=_parse_none_callable_string(hover_text, player_data, ""),
                )
            )
        frame_plots.append(go.Frame(data=frame_tracks, name=str(frame_id)))
        latest_frame_data = frame_data[frame_data[frame_column] == frame_id]
        slider_labels.append(
            str(frame_id) if slider_label_generator is None else slider_label_generator(latest_frame_data)
        )
        # TODO: refactor this with utilities._parse_none_callable_string, if possible
        if events_of_interest is not None:
            if len(event_mapping) == 0:
                event_mapping.append((frame_id, "Reset"))
                continue
            try:
                event_in_frame = events_of_interest(latest_frame_data)
            except TypeError:
                event_in_frame = latest_frame_data[events_of_interest]
            unique_events_in_frame = pd.unique(event_in_frame)
            if len(unique_events_in_frame) != 1:
                raise KeyError(f"Multiple events in frame {frame_id}. Got {unique_events_in_frame}")
            if pd.isnull(unique_events_in_frame[0]) is False and unique_events_in_frame[0].lower() != "none":
                event_mapping.append((frame_id, unique_events_in_frame[0]))
    fig.frames = _safe_add_frames(fig, frame_plots)

    # Add animation controls
    reset_name = fig.frames[0].name if events_of_interest is None else None
    events = None if events_of_interest is None else _make_event_dropdown(event_mapping)
    buttons = _make_control_buttons(seconds_per_frame * 1000, reset_name)

    fig.update_layout(
        updatemenus=[buttons] if events is None else [buttons, events],
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
        margin={"l": 5, "r": 5, "t": 100, "b": 80},
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
    lookup_table: pd.DataFrame,
    num_colors_needed: int,
    null_team_colors: Union[Sequence, str, None] = None,
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
        A pandas DataFrame where the columns are the team abbreviations and the rows
        are the colors. Generally users should
        not be creating this table themselves: instead find the scheme you need in
        ``ptplot._assets`` (for example, NFL team colors are in
        ``ptplot._assets.nfl_teams.TEAM_COLORS``).
    num_colors_needed
        How many colors you need. For example, if you just want to make a scatterplot of
        some aggregated player tracking data and you want to color each point by team color,
        you might only need one color. Alternatively, for animating a single play you may want
        three colors: one for the marker itself, one for the edge of the marker, and one for the
        player's number.
    null_team_colors
        The colors to use if a team abbreviation is null. This often happens when the ball is
        included in the list of identifiers. If ``None``, fills all columns for null abbreviations
        with null values. If a string, fills all columns for null abbreviations with that color.
        If an iterable the same length as ``lookup_table``, will fill based on that lookup table.

    Returns
    -------
    A pandas DataFrame, where the rows correspond to the ``team_abbreviations`` input and the columns
    are ``0``, ``1``, ..., ``num_colors_needed``.

    """
    if num_colors_needed > len(lookup_table):
        raise IndexError(f"{num_colors_needed} colors requested; only {len(lookup_table)} colors available")

    colors_with_nulls = lookup_table.copy(deep=True)
    colors_with_nulls[None] = null_team_colors
    colors_with_nulls[np.nan] = null_team_colors

    # mapped_colors is a dataframe where the columns are the team_abbreviations and the
    # rows are the colors
    mapped_colors = colors_with_nulls[team_abbreviations]

    # Filter to just the rows the user asked for
    mapped_colors = mapped_colors.loc[: (num_colors_needed - 1), :]

    # transpose, reset the index, and return:
    return mapped_colors.T.reset_index(drop=True)


def plot_tracks(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    player_column: str,
    hover_text: Union[None, str, Callable] = None,
    ball_identifier: Union[None, str, Callable] = None,
    home_away_identifier: Union[None, str, Callable] = None,
    team_abbreviations: Union[None, str, Callable] = None,
    team_color_mapping: pd.DataFrame = NFL_TEAM_COLORS,
    fig: Union[None, go.Figure, Field, str] = None,
):
    """Make a static plot showing player tracks over the course of the play.

    Parameters
    ----------
    data
        The data for the given set of tracks.
    x_column
        The name of the column in ``data`` that contains x-axis values
    y_column
        The name of the column in ``data`` that contains y-axis values
    player_column
        The name of the column in ``data`` that contains player names (or whatever will be used
        to split the tracks up)
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
    team_color_mapping
        A dictionary mapping team abbreviations to team colors. Defaults to NFL teams.
    fig
        If an instance of ``plotly.graph_objects.Figure``,
        plot on top of that figure. Otherwise corresponds to the ``sport_field`` keyword argument
        of ``ptplot.plotting.create_field``.

    Returns
    -------
    plotly.graph_objects.Figure
        A Plotly Figure with player tracks shown. If the user passes in a
        Figure, this will be the same Figure.

    Warnings
    --------
    All data must be passed into the function in chronological order, otherwise lines may not be
    drawn correctly.

    """
    # Get all the unique players/balls:
    player_specific_data = data.drop_duplicates(subset=[player_column], ignore_index=True)
    styling_data = pd.DataFrame(
        {
            "is_ball": _parse_none_callable_string(ball_identifier, player_specific_data, False),
            "is_home": _parse_none_callable_string(home_away_identifier, player_specific_data, True),
            "team": _parse_none_callable_string(team_abbreviations, player_specific_data, None),
        },
        index=player_specific_data[player_column].values,
    )
    line_colors = lookup_team_colors(styling_data["team"], team_color_mapping, 1, null_team_colors="brown")
    styling_data["color"] = line_colors.values
    styling_dict = styling_data.to_dict("index")

    mode = "lines"

    if fig is None:
        fig = create_field()
    elif type(fig) in [str, Field]:
        fig = create_field(sport_field=fig)

    player_groups = data.groupby(player_column)
    for player_name, player_data in player_groups:
        player_styles = styling_dict[player_name]
        hover_text_ = _parse_none_callable_string(hover_text, player_data, "")
        fig.add_trace(
            go.Scatter(
                x=player_data[x_column],
                y=player_data[y_column],
                mode=mode,
                text=hover_text_,
                hovertemplate="%{text}<extra></extra>",
                showlegend=False,
                opacity=0.85 if player_styles["is_home"] else 0.6,
                line={
                    "color": player_styles["color"],
                    "width": 3,
                    "dash": "dash" if player_styles["is_ball"] else None,
                },
            )
        )
    return fig


def plot_positions(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    hover_text: Union[None, str, Callable] = None,
    ball_identifier: Union[None, str, Callable] = None,
    home_away_identifier: Union[None, str, Callable] = None,
    team_abbreviations: Union[None, str, Callable] = None,
    uniform_number: Union[None, str, Callable] = None,
    team_color_mapping: pd.DataFrame = NFL_TEAM_COLORS,
    fig: Union[None, go.Figure, Field, str] = None,
):
    """Make a static plot of a frame of data.

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
            hovertemplate="%{hovertext}<extra></extra>",
            showlegend=False,
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
    abbreviation_lookup_table: pd.DataFrame = NFL_TEAM_COLORS,
):
    """generate marker colors based on what team a player is on as well as if they are home or away."""
    # Set defaults:
    home_marker_color = np.tile(np.array(["gainsboro"], dtype="U40"), len(is_home))
    home_marker_edge_color = np.tile(np.array(["darkslategray"], dtype="U40"), len(is_home))
    home_marker_textfont_color = np.tile(np.array(["black"], dtype="U40"), len(is_home))

    away_marker_color = np.tile(np.array(["darkslategray"], dtype="U40"), len(is_home))
    away_marker_edge_color = np.tile(np.array(["gainsboro"], dtype="U40"), len(is_home))
    away_marker_textfont_color = np.tile(np.array(["white"], dtype="U40"), len(is_home))

    if team_abbreviations is not None:
        marker_colors = lookup_team_colors(team_abbreviations, abbreviation_lookup_table, 2).fillna("white")
        marker_colors.columns = ["marker_color", "marker_edge_color"]
        marker_colors["marker_textfont_color"] = "white"
        marker_colors.loc[is_home == 0, "marker_edge_color"] = marker_colors.loc[is_home == 0, "marker_color"]
        marker_colors.loc[is_home == 0, "marker_color"] = "white"
        marker_colors.loc[is_home == 0, "marker_textfont_color"] = "black"
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
    team_color_mapping: pd.DataFrame,
):
    """Generate basic marker color, symbol, and size information."""

    # Marker styling
    marker_color, marker_edge_color, marker_textfont_color = _generate_markers(is_home, team_column, team_color_mapping)
    marker_width = np.tile([2], len(data))
    marker_size = np.tile([16], len(data))
    marker_symbol = np.tile(np.array(["circle"], dtype="U40"), len(data))
    return marker_color, marker_edge_color, marker_textfont_color, marker_width, marker_size, marker_symbol


def _make_event_dropdown(event_mapping, **dropdown_kwargs):
    dropdown_kwargs["active"] = dropdown_kwargs.get("active", 0)
    dropdown_kwargs["direction"] = dropdown_kwargs.get("direction", "down")
    dropdown_kwargs["pad"] = dropdown_kwargs.get("pad", {"b": 10, "t": 30})
    dropdown_kwargs["xanchor"] = dropdown_kwargs.get("xanchor", "right")
    dropdown_kwargs["yanchor"] = dropdown_kwargs.get("yanchor", "top")
    dropdown_kwargs["x"] = dropdown_kwargs.get("x", 1)
    dropdown_kwargs["y"] = dropdown_kwargs.get("y", 1.28)

    events = dict(
        buttons=[
            dict(
                label=event_name,
                method="animate",
                args=[
                    [frame_name],
                    {
                        "frame": {"duration": 10, "redraw": False},
                        "mode": "immediate",
                        "fromcurrent": "true",
                        "transition": {"duration": 10},
                    },
                ],
            )
            for frame_name, event_name in event_mapping
        ],
        **dropdown_kwargs,
    )
    return events


def _make_control_buttons(transition_duration, first_frame_name: Union[str, None] = None, **button_kwargs):
    """Make the play/pause and optional reset buttons for an animation."""
    buttons = [
        dict(
            label="&#9654;",  # play symbol
            method="animate",
            args=[
                None,
                {
                    "frame": {"duration": transition_duration, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": transition_duration, "easing": "linear"},
                    "fromcurrent": True,
                },
            ],
        ),
        dict(
            label="&#10074;&#10074;",  # pause symbol
            method="animate",
            args=[
                [None],
                {
                    "frame": {"duration": 0, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 0},
                },
            ],
        ),
    ]
    if first_frame_name is not None:
        buttons += [
            dict(
                label="&#8634;",  # restart icon
                method="animate",
                args=[
                    [first_frame_name],
                    {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 10}},
                ],
            )
        ]

    button_kwargs["type"] = button_kwargs.get("type", "buttons")
    button_kwargs["direction"] = button_kwargs.get("direction", "left")
    button_kwargs["pad"] = button_kwargs.get("pad", {"b": 10, "t": 30})
    button_kwargs["xanchor"] = button_kwargs.get("xanchor", "left")
    button_kwargs["yanchor"] = button_kwargs.get("yanchor", "top")
    button_kwargs["x"] = button_kwargs.get("x", 0)
    button_kwargs["y"] = button_kwargs.get("y", 1.28)

    buttons = {**button_kwargs, "buttons": buttons}
    return buttons


def _make_sliders(frame_names: Sequence, slider_labels: Sequence, **slider_kwargs):
    """Make the slider widget for an animation."""

    if len(frame_names) != len(slider_labels):
        raise IndexError("Frame names and slider labels must have same length")
    if "steps" in slider_kwargs:
        raise NotImplementedError("Cannot overwrite arguments in the slider steps")
    slider_steps = [
        {
            "args": [
                [frame_name],
                {
                    "frame": {"duration": 100, "redraw": False},
                    "mode": "immediate",
                    "fromcurrent": True,
                    "transition": {"duration": 100},
                },
            ],
            "label": slider_labels[i],
            "method": "animate",
        }
        for i, frame_name in enumerate(frame_names)
    ]

    slider_kwargs["xanchor"] = slider_kwargs.get("xanchor", "left")
    slider_kwargs["yanchor"] = slider_kwargs.get("yanchor", "top")
    slider_kwargs["y"] = slider_kwargs.get("y", 0)
    slider_kwargs["x"] = slider_kwargs.get("x", 0.01)
    slider_kwargs["len"] = slider_kwargs.get("len", 0.98)
    slider_kwargs["pad"] = slider_kwargs.get("pad", {"b": 10, "t": 5})

    sliders = [{**slider_kwargs, "steps": slider_steps}]

    return sliders


def _safe_add_frames(fig: go.Figure, frames: Sequence[go.Frame]):
    """Don't overwrite existing frames, but check and make sure
    that any existing frames have the same length and same ids
    """
    if len(fig.frames) == 0:
        combined_frames = frames
    else:
        if len(fig.frames) != len(frames):
            raise IndexError(f"Frame lengths must match! ({len(fig.frames)}, {len(frames)})")
        combined_frames = []
        for existing_frame, new_frame in zip(fig.frames, frames):
            if existing_frame.name != new_frame.name:
                raise ValueError(
                    f"Frames have different names, which may"
                    f"indicate that they are out of order:"
                    f"({existing_frame.name}, {new_frame.name})"
                )
            combined_frame = go.Frame(data=(existing_frame.data + new_frame.data), name=existing_frame.name)
            combined_frames.append(combined_frame)
    return combined_frames
