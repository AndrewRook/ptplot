from __future__ import annotations

from bokeh.models import HoverTool

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Sequence, Tuple, Union

from .core import Layer


if TYPE_CHECKING:
    from ptplot import PTPlot
    import pandas as pd
    from bokeh.plotting import figure
    from bokeh.models import CustomJS
    from .core import _Metadata


class Hover(Layer):
    def __init__(
            self,
            tooltip_specification: Union[str, List[Tuple[str, str]]],
            plot_name: str,
            tooltip_mappings: Optional[Sequence[str]] = None):
        self.plot_name = plot_name
        self.tooltip_specification = tooltip_specification
        self.tool = HoverTool(names=[plot_name], tooltips=self.tooltip_specification)
        self.tooltip_mappings = [] if tooltip_mappings is None else tooltip_mappings

    def get_mappings(self) -> Sequence[str]:
        return self.tooltip_mappings

    def draw(
            self, ptplot: PTPlot, data: pd.DataFrame, bokeh_figure: figure, metadata: _Metadata
    ) -> None:
        bokeh_figure.add_tools(self.tool)
        return None