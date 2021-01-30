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
        with pytest.raises(ValueError, match="too many values to unpack"):
            plotting.lookup_team_colors(team_abbreviations, team_color_map, 3)