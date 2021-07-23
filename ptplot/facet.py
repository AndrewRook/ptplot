from __future__ import annotations

import math

from .core import Layer

from typing import TYPE_CHECKING, Any, Iterator, Optional, Sequence, Tuple

if TYPE_CHECKING:
    import pandas as pd

    from bokeh.plotting import figure
    from ptplot import PTPlot
    from ptplot.core import _Metadata


class Facet(Layer):
    """Break a dataset into multiple subplots ("facets").

    Note that you can't have more than one Facet on a visualization.

    Parameters
    ----------
    facet_mapping : The mapping to use to split the dataset into facets.
    num_col, num_row : The number of columns/rows to split the dataset into. Only
       one of the two variables should be defined.
    """

    def __init__(self, facet_mapping: str, num_col: Optional[int] = None, num_row: Optional[int] = None):
        self.facet_mapping = facet_mapping
        self.num_col = num_col
        self.num_row = num_row
        if self.num_row is not None and self.num_col is not None:
            raise ValueError("Can only specify one of num_col or num_row")

    def get_mappings(self) -> Sequence[str]:
        return [self.facet_mapping]

    def faceting(self, data: pd.DataFrame) -> Iterator[Tuple[Any, pd.DataFrame]]:
        groups = data.groupby(self.facet_mapping, sort=False)
        if self.num_col is not None:
            self.num_row = math.ceil(len(groups) / self.num_col)
        elif self.num_row is not None:
            self.num_col = math.ceil(len(groups) / self.num_row)
        else:
            self.num_row = len(groups)
            self.num_col = 1
        return groups

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata) -> None:
        # This will get run multiple times per aesthetic, but the title ought to be the same
        # every time so this should be ok.
        facet_value = data[self.facet_mapping].unique()[0]
        bokeh_figure.title.text = str(facet_value)
