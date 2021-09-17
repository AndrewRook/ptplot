from bokeh.models.glyphs import Circle
from bokeh.core.property.dataspec import field
from bokeh.core.properties import AngleSpec


class Pick(Circle):
    __implementation__ = "pick.ts"
    _args = ("x", "y", "rot")

    rot = AngleSpec(default=field("rot"))
