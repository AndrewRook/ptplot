from __future__ import annotations

import pandas as pd
import patsy

from bokeh.models import ColumnDataSource
from typing import TYPE_CHECKING, Optional

from .layer import Layer


if TYPE_CHECKING:
    from .ptplot import PTPlot


class PlayerPlot(Layer):
    def __init__(self, x: str, y: str, frame_filter: Optional[str] = None):
        self.x = x
        self.y = y
        self.frame_filter = frame_filter

    def __radd__(self, ptplot: PTPlot):
        data = ptplot.data
        if self.frame_filter:
            data = data[_apply_patsy_string(data, self.frame_filter, allow_arithmetic=False)]

        source = ColumnDataSource(data)
        ptplot.figure.circle(x=self.x, y=self.y, source=source, fill_color="red", radius=1)

        #breakpoint()


def _apply_patsy_string(
        data: pd.DataFrame, patsy_string: str,
        allow_conditionals: bool = True,
        allow_arithmetic: bool = True
):
    processed_string_data = patsy.dmatrix(
        f"I({patsy_string}) - 1",
        data,
        NA_action=patsy.NAAction(NA_types=[]),
        return_type="dataframe"
    )
    if not allow_conditionals and len(processed_string_data.columns) == 2:
        raise ValueError(f"{patsy_string}: Conditional statements not allowed")
    if not allow_arithmetic and len(processed_string_data.columns) == 1:
        raise ValueError(f"{patsy_string}: Arithmetic statements not allowed")

    final_data = (
        processed_string_data[processed_string_data.columns[0]]
        if len(processed_string_data.columns) == 1 # pure arithmetic
        else processed_string_data[processed_string_data.columns[1]].astype(bool) # conditional
    )
    return final_data
