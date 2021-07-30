import os
#os.environ["BOKEH_MINIFIED"] = "false"
#os.environ["BOKEH_PRETTY"] = "true"

import pandas as pd

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show

from ptplot.bezier_fill import BezierFill


data = pd.DataFrame({"x": [1, 2, 3], "y1": [1, 2, 3], "y2": [6, 5, 4]})
data["cx0"] = data.x - 0.5
data["cx1"] = data.x + 0.5
data["cy_1"] = data.y1 + 2
data["cy_2"] = data.y2 + 2


source = ColumnDataSource(data)


plot = figure(height=200, x_range=(0, 4), y_range=(0, 7))

# glyph = BezierFill(
#     x0="x", x1="x", y0="y2", y1="y2", cx0="cx0", cx1="cx1", cy0="cy_2", cy1="cy_2",
#     line_color="red", fill_color="green"
# )
glyph = BezierFill(
    x0="x", y0="y2",
    line_color="red", fill_color="green"
)
plot.add_glyph(source, glyph)
plot.bezier(x0="x", x1="x", y0="y1", y1="y1", cx0="cx0", cx1="cx1", cy0="cy_1", cy1="cy_1", source=source)

show(plot)
