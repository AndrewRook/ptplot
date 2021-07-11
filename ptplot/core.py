from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

import pandas as pd
from bokeh.plotting import figure

from typing import TYPE_CHECKING, Any, Callable, Iterator, Mapping, Sequence, Optional, Tuple

if TYPE_CHECKING:
    from bokeh.models import CustomJS, GlyphRenderer
    from ptplot import PTPlot


@dataclass
class _Metadata:
    label: Optional[str] = ""
    is_home: bool = True
    color_list: Sequence[str] = ("black", "gray")
    marker: Optional[Callable[[figure], Callable[..., GlyphRenderer]]] = None


class Layer(ABC):
    def get_mappings(self) -> Sequence[str]:
        return []

    def draw(
        self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata
    ) -> Optional[Sequence[Callable[[str, Any], CustomJS]]]:
        pass


class _Aesthetics(Layer):
    team_color_mapping: Mapping[str, Sequence[str]] = {}
    ball_colors: Sequence[str] = ("black", "black")
    ball_marker_generator: Optional[Callable[[figure], Callable[..., GlyphRenderer]]] = None

    def __init__(
        self,
        team_ball_mapping: Optional[str] = None,
        home_away_mapping: Optional[str] = None,
        ball_identifier: Optional[str] = None,
    ):
        self.team_ball_mapping = team_ball_mapping
        self.home_away_mapping = home_away_mapping
        self.ball_identifier = ball_identifier

    def get_mappings(self) -> Sequence[str]:
        mappings = []
        if self.team_ball_mapping is not None:
            mappings.append(self.team_ball_mapping)
        if self.home_away_mapping is not None:
            mappings.append(self.home_away_mapping)
        return mappings

    def map_aesthetics(self, data: pd.DataFrame) -> Iterator[Tuple[pd.DataFrame, _Metadata]]:
        if self.team_ball_mapping is not None:
            team_ball_groups = data.groupby(self.team_ball_mapping)
            for team_ball_name, team_ball_data in team_ball_groups:
                if self.ball_identifier is not None and team_ball_name == self.ball_identifier:
                    yield team_ball_data, _Metadata(
                        label=team_ball_name,
                        is_home=True,
                        # have to access the __func__ method directly to avoid needing to wrap all the
                        # methods in staticmethod decorators
                        # Also need to ignore mypy because it doesn't like doing that.
                        color_list=self.ball_colors,
                        marker=self.ball_marker_generator.__func__,  # type: ignore
                    )
                else:
                    team_color_list = self.team_color_mapping[team_ball_name]
                    if self.home_away_mapping is not None:
                        home_away_groups = team_ball_data.groupby(self.home_away_mapping)
                        for is_home, home_away_data in home_away_groups:
                            yield home_away_data, _Metadata(
                                label=team_ball_name, is_home=is_home, color_list=team_color_list
                            )
                    else:
                        yield team_ball_data, _Metadata(label=team_ball_name, is_home=True, color_list=team_color_list)
        else:
            if self.home_away_mapping is not None:
                home_away_groups = data.groupby(self.home_away_mapping)
                for is_home, home_away_data in home_away_groups:
                    yield home_away_data, _Metadata(is_home=is_home)
            else:
                yield data, _Metadata()
