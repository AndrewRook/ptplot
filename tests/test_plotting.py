import numpy as np
import pandas as pd
import pytest

from ptplot import plotting
from ptplot._assets.nfl_teams import TeamColors


@pytest.mark.parametrize("constructor", [np.array, pd.Series, list])
class TestLookupTeamColors:

    @pytest.fixture()
    def team_color_map(self):
        return {
            "NYJ": TeamColors(["a", "b", "c"], ["d", "e", "f"]),
            "CLE": TeamColors(["g", "h"], ["i", "j"]),
            "CHI": TeamColors(["k", "l", "m"], ["n", "o"])
        }

    def test_raises_error_if_too_many_colors_are_requested(self, team_color_map, constructor):
        team_abbreviations = constructor(["NYJ", "CLE", "NYJ"])
        with pytest.raises(IndexError, match="index out of range"):
            plotting.lookup_team_colors(team_abbreviations, team_color_map, 3)

    def test_raises_error_if_too_many_away_team_colors_are_requested(self, team_color_map, constructor):
        team_abbreviations = constructor(["CHI", "CHI"])
        home_away_indicator = constructor([False, False])
        # Passes when assuming home team:
        #breakpoint()
        plotting.lookup_team_colors(team_abbreviations, team_color_map, 3)
        # Fails when using the away team, which has fewer colors
        with pytest.raises(IndexError, match="index out of range"):
            plotting.lookup_team_colors(team_abbreviations, team_color_map, 3, team_is_home_flag=home_away_indicator)

    def test_works_no_home_away_data(self, team_color_map, constructor):
        team_abbreviations = constructor(["NYJ", "CLE", "NYJ"])
        primary_colors, secondary_colors = plotting.lookup_team_colors(
            team_abbreviations, team_color_map, 2
        )
        assert primary_colors == ("a", "g", "a")
        assert secondary_colors == ("b", "h", "b")

    def test_works_with_home_away_data(self, team_color_map, constructor):
        team_abbreviations = constructor(["NYJ", "CLE", "NYJ"])
        home_away_indicator = constructor([False, True, False])
        primary_colors, secondary_colors = plotting.lookup_team_colors(
            team_abbreviations, team_color_map, 2, team_is_home_flag=home_away_indicator
        )
        assert primary_colors == ("d", "g", "d")
        assert secondary_colors == ("e", "h", "e")
