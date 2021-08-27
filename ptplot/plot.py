from __future__ import annotations

from bokeh.models import ColumnDataSource, CustomJS
from bokeh.plotting._decorators import glyph_method
from typing import TYPE_CHECKING, Any, Callable, Sequence, Optional

from ptplot.callback import FIND_CURRENT_FRAME, FIND_ALL_FRAMES_UP_TO_CURRENT_FRAME
from ptplot.core import Layer, _Metadata
from ptplot.pick import Pick
from ptplot.utils import _union_kwargs

if TYPE_CHECKING:
    from bokeh.plotting import figure
    from bokeh.models import GlyphRenderer
    from .ptplot import PTPlot
    import pandas as pd


class Tracks(Layer):
    """
    Generate tracks showing position over time for players and/or the ball.

    For a static image the tracks are just lines. For an animated image the lines will grow over time
    as the players and the ball move.

    Parameters
    ----------
    x : The mapping to be used as the x (horizontal) coordinate for the tracks.
    y : The mapping to be used as the y (vertical) coordinate for the tracks.
    track_mapping : the mapping to group the data into individual tracks. Usually the column that corresponds
        to each player (e.g. player name, jersey number).
    animate : If True and an Animation layer is provided to the plot, animate the tracks. If False, show the
        full tracks even if an Animation layer is provided.
    name : If you plan on using the Hover layer, provide a name for the layer in order to assign hoverlabels
        to the glyphs drawn by this layer.
    kwargs : Any additional keyword arguments to bokeh.figure.lines.
    """

    def __init__(
        self, x: str, y: str, track_mapping: str, animate: bool = True, name: Optional[str] = None, **kwargs: Any
    ):
        self.x = x
        self.y = y
        self.track_mapping = track_mapping
        self.animate = animate
        self.callback = FIND_ALL_FRAMES_UP_TO_CURRENT_FRAME
        self.name = name
        self.kwargs = kwargs

    def get_mappings(self) -> Sequence[str]:
        return [self.x, self.y, self.track_mapping]

    def set_up_animation(self, graphics: GlyphRenderer) -> Callable[[str, Any], CustomJS]:
        source = graphics.data_source
        full_source = ColumnDataSource(source.data)

        def animate(frame_column: str, initial_frame: Any) -> CustomJS:
            is_in_initial_frame = source.data[frame_column] <= initial_frame
            initial_data = {column: source.data[column][is_in_initial_frame] for column in source.data}
            source.data = initial_data

            callback = CustomJS(
                args={"source": source, "full_source": full_source, "frame_column": frame_column}, code=self.callback
            )
            return callback

        return animate

    def draw(
        self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata
    ) -> Optional[Sequence[Callable[[str, Any], CustomJS]]]:

        line_color = metadata.color_list[0] if metadata.is_home is True else metadata.color_list[1]
        groups = data.groupby(self.track_mapping)
        all_graphics = []
        for group_name, group_data in groups:
            source = ColumnDataSource(group_data)
            kwargs = _union_kwargs(
                {
                    "x": self.x,
                    "y": self.y,
                    "source": source,
                    "line_color": line_color,
                    "legend_label": metadata.label,
                    "name": self.name,
                },
                self.kwargs,
            )
            graphics = bokeh_figure.line(**kwargs)
            all_graphics.append(graphics)

        if self.animate is False:
            return None
        else:
            return [self.set_up_animation(graphics) for graphics in all_graphics]


class Positions(Layer):
    """
    Generate markers showing the positions of players and/or the ball.

    If a special marker has not been specified as part of an Aesthetics, then
    the default circle will be used.

    Optionally, a mapping can be specified to plot text on top of the markers,
    designed for showing jersey numbers. Note that there are no guardrails in place
    to ensure that the text stays within the markers, although sensible defaults have
    been chosen where two-digit numbers look reasonable at the default zoom level.

    Parameters
    ----------
    x : The mapping to be used as the x (horizontal) coordinate for the tracks.
    y : The mapping to be used as the y (vertical) coordinate for the tracks.
    number : If set, a mapping indicating what text should be shown on top of the markers.
    frame_filter : If set, a True/False mapping of the data used to determine a specific frame
        to display at all times, even if an Animation is set.
    marker_radius : The size (in data units, e.g. yards for American Football) of the radius of the
        marker.
    name : If you plan on using the Hover layer, provide a name for the layer in order to assign hoverlabels
        to the glyphs drawn by this layer.
    kwargs : Any additional keyword arguments to the glyph renderer for the markers. Note that these do not
        apply to any text on top of the markers
    """

    def __init__(
        self,
        x: str,
        y: str,
        orientation: Optional[str] = None,
        number: Optional[str] = None,
        frame_filter: Optional[str] = None,
        marker_radius: float = 1,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.number = number
        self.frame_filter = frame_filter
        self.callback = FIND_CURRENT_FRAME
        self.marker_radius = marker_radius
        self.name = name
        self.kwargs = kwargs

    def get_mappings(self) -> Sequence[str]:
        mappings = [self.x, self.y]

        if self.orientation is not None:
            mappings += [self.orientation]
        if self.frame_filter is not None:
            mappings += [self.frame_filter]
        if self.number is not None:
            mappings += [self.number]
        return mappings

    def set_up_animation(self, graphics: GlyphRenderer) -> Callable[[str, Any], CustomJS]:
        source = graphics.data_source
        full_source = ColumnDataSource(source.data)

        def animate(frame_column: str, initial_frame: Any) -> CustomJS:
            is_in_initial_frame = source.data[frame_column] <= initial_frame
            initial_data = {column: source.data[column][is_in_initial_frame] for column in source.data}
            source.data = initial_data

            callback = CustomJS(
                args={"source": source, "full_source": full_source, "frame_column": frame_column}, code=self.callback
            )
            return callback

        return animate

    def draw(
        self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata
    ) -> Optional[Sequence[Callable[[str, Any], CustomJS]]]:

        # If you have multiple frames but only want to show one (even in an animation):
        if self.frame_filter is not None:
            data = data[data[self.frame_filter]]
        source = ColumnDataSource(data)

        all_kwargs = _union_kwargs(
            {"x": self.x, "y": self.y, "source": source, "legend_label": metadata.label, "name": self.name}, self.kwargs
        )

        if metadata.marker is not None:
            graphics = metadata.marker(bokeh_figure)(**all_kwargs)
        else:
            fill_color, line_color = (
                metadata.color_list if metadata.is_home is True else ["white", metadata.color_list[0]]
            )
            player_kwargs = _union_kwargs(
                {"fill_color": fill_color, "line_color": line_color, "radius": self.marker_radius}, all_kwargs
            )
            if self.orientation is None:
                graphics = bokeh_figure.circle(**player_kwargs)
            else:
                # This is a kludge to let me take advantage of the bokeh all-in-one
                # figure.plot_name syntax, which handles adding the source, making the legends,
                # etc.
                def pick(**kwargs: Any) -> None:
                    pass

                decorated_pick = glyph_method(Pick)(pick)

                player_kwargs = _union_kwargs({"rot": self.orientation}, player_kwargs)
                graphics = decorated_pick(bokeh_figure, **player_kwargs)

        if self.number is not None:
            # https://github.com/bokeh/bokeh/issues/2439#issuecomment-447498732
            text_color = "white" if metadata.is_home is True else "black"

            # This is a total kludge to scale font size up and down with plot size,
            # based on a font size I found to work reasonably well with two-digit
            # numbers
            pixels_per_data_unit = bokeh_figure.height / abs(bokeh_figure.y_range.end - bokeh_figure.y_range.start)
            font_size = pixels_per_data_unit * self.marker_radius

            bokeh_figure.text(
                x=self.x,
                y=self.y,
                text=self.number,
                source=source,
                text_color=text_color,
                text_align="center",
                text_baseline="middle",
                text_font_size=f"{font_size:.2f}px",
            )
            # Don't need to set up a separate animation for the numbers because the source, view, and callback are
            # all the same
        if self.frame_filter is not None:
            return None
        else:
            return [self.set_up_animation(graphics)]
