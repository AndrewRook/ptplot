from bokeh.core.properties import Include, NumberSpec
from bokeh.core.property.dataspec import field
from bokeh.core.property_mixins import LineProps, FillProps
from bokeh.models import Glyph


class BezierFill(Glyph):
    __implementation__ = "bezier_fill.ts"

    _args = ("x0", "y0", "x1", "y1", "cx0", "cy0", "cx1", "cy1")

    x0 = NumberSpec(default=field("x0"), help="""
    The x-coordinates of the starting points.
    """)

    y0 = NumberSpec(default=field("y0"), help="""
    The y-coordinates of the starting points.
    """)

    cx0 = NumberSpec(default=field("cx0"), help="""
    The x-coordinates of first control points.
    """)

    cy0 = NumberSpec(default=field("cy0"), help="""
    The y-coordinates of first control points.
    """)

    cx1 = NumberSpec(default=field("cx1"), help="""
    The x-coordinates of second control points.
    """)

    cy1 = NumberSpec(default=field("cy1"), help="""
    The y-coordinates of second control points.
    """)

    line_props = Include(LineProps, use_prefix=False, help="""
    The %s values for the Bezier curves.
    """)

    fill_props = Include(FillProps, use_prefix=False, help="""
    The %s values for the Bezier curves.
    """)