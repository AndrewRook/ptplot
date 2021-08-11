from bokeh.models.glyph import LineGlyph, FillGlyph
from bokeh.core.property.dataspec import field
from bokeh.core.properties import AngleSpec, Include, NullDistanceSpec, NumberSpec
from bokeh.core.property_mixins import LineProps, FillProps


class Pick(LineGlyph, FillGlyph):
    __implementation__ = "pick.ts"
    _args = ("x", "y", "rot")

    radius = NullDistanceSpec()
    x = NumberSpec(default=field("x"))
    y = NumberSpec(default=field("y"))
    rot = AngleSpec(default=field("rot"))

    line_props = Include(
        LineProps,
        use_prefix=False,
        help="""
    The {prop} values for the Pick.
    """,
    )

    fill_props = Include(
        FillProps,
        use_prefix=False,
        help="""
    The {prop} values for the Pick.
    """,
    )
