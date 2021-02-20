import pandas as pd


_TEAM_COLORS = {
    "ARI": ["#97233f", "black"],
    "ATL": ["#a71930", "#a5acaf", "black"],
    "BAL": ["#241773", "#9e7c0c", "black"],
    "BUF": ["#00338d", "#c60c30"],
    "CAR": ["#0085ca", "#bfc0bf", "black"],
    "CHI": ["#0b162a", "#c83803"],
    "CIN": ["#fb4f14", "black"],
    "CLE": ["#311d00", "#ff3c00"],
    "DAL": ["#002244", "#869397", "#00338d"],
    "DEN": ["#fb4f14", "#002244"],
    "DET": ["#0076b6", "#b0b7bc"],
    "GB": ["#203731", "#ffb612"],
    "HOU": ["#03202f", "#a71930"],
    "IND": ["#002c5f", "#a5acaf"],
    "JAX": ["#006778", "#9f792c", "black"],
    "KC": ["#e31837", "#ffb612"],
    "LAC": ["#0073cf", "#ffb612", "#002244"],
    "LAR": ["#002244", "#b3995d"],
    "LV": ["black", "#a5acaf"],
    "MIA": ["#008e97", "#f26a24", "#005778"],
    "MIN": ["#4f2683", "#ffc62f"],
    "NE": ["#002244", "#c60c30", "#b0b7bc"],
    "NO": ["black", "#d3bc8d"],
    "NYG": ["#0b2265", "#a71930", "#a5acaf"],
    "NYJ": ["#003f2d", "white"],
    "PHI": ["#004c54", "#a5acaf", "black"],
    "PIT": ["black", "#ffb612", "#c60c30", "#00539b"],
    "SF": ["#aa0000", "#b3995d"],
    "SEA": ["#002244", "#69be28", "#a5acaf"],
    "TB": ["#d50a0a", "#34302b", "#ff7900"],
    "TEN": ["#002244", "#4b92db", "#c60c30", "#a5acaf"],
    "WAS": ["#773141", "#ffb612"],
    "OAK": ["black", "#a5acaf"],
    "STL": ["#002244", "#b3995d"],
}

_max_number_colors = max(len(color_list) for _, color_list in _TEAM_COLORS.items())
TEAM_COLORS = pd.DataFrame(
    {team: color_list + [None] * (_max_number_colors - len(color_list)) for team, color_list in _TEAM_COLORS.items()}
)
