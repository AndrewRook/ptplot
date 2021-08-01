from bokeh.core.properties import AngleSpec, DistanceSpec, Include, Float, NumberSpec
from bokeh.core.property.dataspec import field
from bokeh.core.property_mixins import LineProps, FillProps
from bokeh.models import Bezier


class BezierFill(Bezier):
    __implementation__ = "bezier_fill.ts"

    fill_props = Include(FillProps, use_prefix=False, help="""
    The %s values for the Bezier curves.
    """)