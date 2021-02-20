import numpy as np
import pandas as pd
import pytest

from ptplot import plotting


@pytest.mark.parametrize("constructor", [np.array, pd.Series, list])
class TestLookupTeamColors:

    @pytest.fixture()
    def team_color_map(self):
        return pd.DataFrame({
            "NYJ": ["a", "b", "c"],
            "CLE": ["g", "h", None],
            "CHI": ["k", "l", "m"]
        })

    def test_raises_error_if_too_many_colors_are_requested(self, team_color_map, constructor):
        team_abbreviations = constructor(["NYJ", "CLE", "NYJ"])
        with pytest.raises(IndexError, match="4 colors requested; only 3 colors available"):
            plotting.lookup_team_colors(team_abbreviations, team_color_map, 4)

    def test_works_general_case(self, team_color_map, constructor):
        team_abbreviations = constructor(["NYJ", "CLE", "NYJ"])
        colors = plotting.lookup_team_colors(
            team_abbreviations, team_color_map, 2
        )
        expected_colors = pd.DataFrame({
            0: ["a", "g", "a"],
            1: ["b", "h", "b"]
        })
        pd.testing.assert_frame_equal(colors, expected_colors)

    def test_works_with_null_abbreviation(self, team_color_map, constructor):
        team_abbreviations = constructor(["NYJ", "CLE", None])
        colors = plotting.lookup_team_colors(
            team_abbreviations, team_color_map, 2, null_team_colors="green"
        )
        expected_colors = pd.DataFrame({
            0: ["a", "g", "green"],
            1: ["b", "h", "green"]
        })
        pd.testing.assert_frame_equal(colors, expected_colors)
