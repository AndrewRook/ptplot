from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

import pandas as pd
from bokeh.plotting import figure

from typing import TYPE_CHECKING, Callable, Sequence, Optional

if TYPE_CHECKING:
    from ptplot import PTPlot


@dataclass
class _Metadata:
    label: Optional[str] = ""
    is_home: bool = True
    color_list: Sequence[str] = ("black", "gray")
    marker: Optional[Callable] = None


class Layer(ABC):

    def get_mappings(self) -> Sequence[str]:
        return []

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata):
        pass

    def __radd__(self, ptplot: PTPlot):
        pass


def _generate_aesthetics(
        team_color_mapping: dict, ball_colors: Optional[Sequence] = None,
        ball_marker_generator: Optional[Callable] = None
):
    class Aesthetics(Layer):
        def __init__(self, team_ball_mapping=None, home_away_mapping=None, ball_identifier=None):
            self.team_ball_mapping = team_ball_mapping
            self.home_away_mapping = home_away_mapping
            self.ball_identifier = ball_identifier
            self.ball_colors = ball_colors
            self.team_color_mapping = team_color_mapping
            self._ball_marker = ball_marker_generator

        def get_mappings(self):
            mappings = []
            if self.team_ball_mapping is not None:
                mappings.append(self.team_ball_mapping)
            if self.home_away_mapping is not None:
                mappings.append(self.home_away_mapping)
            return mappings

        def map_aesthetics(self, data: pd.DataFrame):
            if self.team_ball_mapping is not None:
                team_ball_groups = data.groupby(self.team_ball_mapping)
                for team_ball_name, team_ball_data in team_ball_groups:
                    if self.ball_identifier is not None and team_ball_name == self.ball_identifier:
                        yield team_ball_data, _Metadata(
                            label=team_ball_name, is_home=True,
                            color_list=self.ball_colors, marker=self._ball_marker
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
                            yield team_ball_data, _Metadata(
                                label=team_ball_name, is_home=True, color_list=team_color_list
                            )
            else:
                if self.home_away_mapping is not None:
                    home_away_groups = data.groupby(self.home_away_mapping)
                    for is_home, home_away_data in home_away_groups:
                        yield home_away_data, _Metadata(
                            is_home=is_home
                        )
                else:
                    yield data, _Metadata()
    return Aesthetics
