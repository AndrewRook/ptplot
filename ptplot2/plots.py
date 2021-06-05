from __future__ import annotations

import pandas as pd
import patsy

from bokeh.models import ColumnDataSource
from typing import TYPE_CHECKING, Optional

from .layer import Layer


if TYPE_CHECKING:
    from .ptplot import PTPlot


class PlayerPlot(Layer):
    def __init__(
            self, x: str, y: str,
            team: Optional[str] = None,
            team_mapping: Optional[pd.DataFrame] = None,
            home_flag: Optional[str] = None,
            frame_filter: Optional[str] = None
    ):
        self.x = x
        self.y = y
        if team is not None and team_mapping is None:
            raise KeyError("Must specify a team mapping if you specify a team column")
        self.team = team
        self.team_mapping = team_mapping
        self.home_flag = home_flag
        self.frame_filter = frame_filter

    def __radd__(self, ptplot: PTPlot):
        data = ptplot.data.copy(deep=True)
        if self.frame_filter:
            data = data[_apply_patsy_string(data, self.frame_filter, allow_arithmetic=False)]

        data["_home_flag"] = (
            True
            if not self.home_flag
            else _apply_patsy_string(data, self.home_flag, allow_arithmetic=False)
        )
        data["_team"] = (
            "N/A"
            if not self.team
            else _apply_patsy_string(data, self.team, allow_conditional=False)
        )
        data_groups = data.groupby(["_team", "_home_flag"], dropna=False)
        for (team, is_home), group in data_groups:
            breakpoint()
            colors = ["black", "grey"] if team == "N/A" else self.team_mapping[team].values
            if is_home:
                fill_color = colors[0]
                line_color = colors[1]
            else:
                fill_color = colors[1]
                line_color = colors[0]
            source = ColumnDataSource(group)
            ptplot.figure.circle(
                x=self.x, y=self.y, source=source,
                fill_color=fill_color, line_color=line_color, radius=1, line_width=2
            )

            #breakpoint()
        # data = data.reset_index(drop=True)
        # data["color"] = "black"
        # data.loc[0, "color"] = "red"
        # print(data[["x", "y", "color"]])
        #
        #
        # source = ColumnDataSource(data)
        # ptplot.figure.circle(x=self.x, y=self.y, source=source, fill_color="color", radius=1)

        #breakpoint()


def _apply_patsy_string(
        data: pd.DataFrame, patsy_string: str,
        allow_conditional: bool = True,
        allow_arithmetic: bool = True
):
    if patsy_string in data.columns:
        return data[patsy_string]

    processed_string_data = patsy.dmatrix(
        f"I({patsy_string}) - 1",
        data,
        NA_action=patsy.NAAction(NA_types=[]),
        return_type="dataframe"
    )
    if not allow_conditional and len(processed_string_data.columns) == 2:
        raise ValueError(f"{patsy_string}: Conditional statements not allowed")
    if not allow_arithmetic and len(processed_string_data.columns) == 1:
        raise ValueError(f"{patsy_string}: Arithmetic statements not allowed")

    final_data = (
        processed_string_data[processed_string_data.columns[0]]
        if len(processed_string_data.columns) == 1 # pure arithmetic
        else processed_string_data[processed_string_data.columns[1]].astype(bool) # conditional
    )
    return final_data
