from dataclasses import dataclass

from typing import Sequence

@dataclass
class TeamColors:
    home: Sequence[str]
    away: Sequence[str]


TEAM_COLORS = {
    # "ARI": TeamColors(
    #
    # ),
    # "ATL": TeamColors(
    #
    # ),
    "CHI": TeamColors(
        ["rgb(200, 56, 3)", "rgb(11, 22, 42)", "white"],
        ["white", "rgb(200, 56, 3)", "rgb(11, 22, 42)"]
    ),
    "GB": TeamColors(
        ["rgb(28, 45, 37)", "rgb(238, 173, 30), white"],
        ["white", "rgb(28, 45, 37)", "rgb(238, 173, 30)"]
    ),
    # "NE": TeamColors(
    #
    # ),
    # "NYJ": TeamColors(
    #
    # ),
}