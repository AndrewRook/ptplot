from __future__ import annotations

from bokeh.models import HoverTool

from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple, Union

from .core import Layer


if TYPE_CHECKING:
    from ptplot import PTPlot
    import pandas as pd
    from bokeh.plotting import figure
    from .core import _Metadata


class Hover(Layer):
    """Add a hoverlabel to the visualization. Hoverlabels will appear as mouseover
    events. While they are usually used for simply identifying data points, they can be almost arbitrarily
    complex. See https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#hovertool
    for details (and inspiration!).

    Note that, conceptually, multiple Hover layers can be used in the same visualization; however this has not
    been thoroughly tested so unexpected behavior may occur.

    Parameters
    ----------
    tooltip_specification : The definition for the tooltip display. It can be anything that can be passed
        as the tooltips argument to Bokeh's HoverTool.
    plot_name : The name you assigned to the specific plotting layer that you wish the hoverlabel to be attached to
        (ie what glyphs you want the label to pop up on when moused over).
    tooltip_mappings : The mappings for any columns that you want to use in the tooltips (unfortunately it is
        not yet possible to pull those mappings directly from the tooltip_specification input).
    """

    def __init__(
        self,
        tooltip_specification: Union[str, List[Tuple[str, str]]],
        plot_name: str,
        tooltip_mappings: Optional[Sequence[str]] = None,
    ):
        self.plot_name = plot_name
        self.tooltip_specification = tooltip_specification
        self.tool = HoverTool(names=[plot_name], tooltips=self.tooltip_specification)
        self.tooltip_mappings = [] if tooltip_mappings is None else tooltip_mappings

    def get_mappings(self) -> Sequence[str]:
        return self.tooltip_mappings

    def draw(self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata) -> None:
        bokeh_figure.add_tools(self.tool)
        return None
