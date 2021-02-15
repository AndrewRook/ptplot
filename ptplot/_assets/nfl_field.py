"""Information for drawing an NFL field. All units are in yards"""

from svgpathtools import parse_path

from ..utilities import get_path_midpoint, make_vline, make_hline
from .core import Field

FIELD_LENGTH = 120
FIELD_WIDTH = 53.3
BACKGROUND_COLOR = "rgb(195,217,192)"  # "rgb(62, 126, 0)"

"""In order to have the field numbers (the 10, 20, 30, 40, 50) scale properly with
field size, they need to be rendered as SVG shapes. This dictionary maps the numbers
to SVG values, based on the Alice font and converted by
https://danmarshall.github.io/google-font-to-svg-path/. I think I used size 10, but I no
longer remember :/
"""
FIELD_NUMBER_PATHS = {
    "zero": parse_path(
        "M 1.19 2.751 Q 0.8 2.751 0.533 2.561 Q 0.265 2.371 0.133 2.056 Q 0 1.741 0 1.371 "
        "Q 0 0.996 0.133 0.686 Q 0.265 0.376 0.533 0.188 Q 0.8 0.001 1.19 0.001 Q 1.56 0.001 1.83 0.191 "
        "Q 2.1 0.381 2.24 0.696 Q 2.38 1.011 2.38 1.371 Q 2.38 1.731 2.24 2.046 Q 2.1 2.361 1.83 2.556 "
        "Q 1.56 2.751 1.19 2.751 Z M 1.195 2.566 Q 1.53 2.566 1.715 2.256 Q 1.9 1.946 1.9 1.371 "
        "Q 1.9 0.796 1.715 0.491 Q 1.53 0.186 1.195 0.186 Q 0.85 0.186 0.665 0.488 Q 0.48 0.791 0.48 1.371 "
        "Q 0.48 1.951 0.665 2.258 Q 0.85 2.566 1.195 2.566 Z"
    ),
    "one": parse_path(
        "M 0.713,0.6800000000000002 L 0.713,1.72 A 3.257,3.257 180.0 0,1 0.714,1.789 "
        "A 1.126,1.126 180.0 0,1 0.691,2.057 Q 0.663,2.16 0.593,2.19 "
        "Q 0.523,2.2199999999999998 0.363,2.2199999999999998 L 0.118,2.2199999999999998 "
        "A 0.095,0.095 180.0 0,0 0.028,2.34 Q 0.033,2.415 0.058,2.432 Q 0.083,2.45 0.121,2.45 "
        "L 0.173,2.45 Q 0.383,2.45 0.583,2.517 Q 0.783,2.585 1.018,2.68 Q 1.048,2.69 1.068,2.69 "
        "Q 1.148,2.69 1.148,2.5749999999999997 L 1.148,0.6800000000000002 "
        "Q 1.148,0.45999999999999996 1.201,0.36499999999999977 Q 1.253,0.27 1.366,0.2450000000000001 "
        "Q 1.478,0.21999999999999975 1.728,0.21999999999999975 L 1.778,0.21999999999999975 "
        "Q 1.818,0.21999999999999975 1.836,0.19999999999999973 "
        "Q 1.853,0.18000000000000016 1.858,0.1200000000000001 Q 1.858,0.0 1.768,0.0 "
        "Q 1.408,0.015000000000000124 0.928,0.015000000000000124 Q 0.453,0.015000000000000124 0.093,0.0 "
        "A 0.095,0.095 180.0 0,0 0.003,0.12 Q 0.008,0.18000000000000016 0.026,0.19999999999999973 "
        "Q 0.043,0.21999999999999975 0.083,0.21999999999999975 Q 0.363,0.21999999999999975 0.481,0.242 "
        "Q 0.598,0.2650000000000001 0.656,0.3599999999999999 Q 0.713,0.45500000000000007 0.713,0.68 Z"
    ),
    "two": parse_path(
        "M 0.447,0.3799999999999999 L 0.447,0.355 L 1.787,0.355 A 0.449,0.449 180.0 0,0 1.969,0.32699999999999996 "
        "Q 2.027,0.2999999999999998 2.027,0.17999999999999972 Q 2.027,0.0 1.852,0.0 L 0.177,0.0 "
        "Q 0.002,0.0 0.002,0.17999999999999972 Q 0.007,0.2849999999999997 0.059,0.3500000000000001 "
        "Q 0.112,0.41500000000000004 0.232,0.4950000000000001 Q 0.627,0.76 0.844,0.9319999999999999 "
        "Q 1.062,1.105 1.237,1.3699999999999999 Q 1.412,1.635 1.412,1.9649999999999999 "
        "Q 1.412,2.205 1.284,2.3369999999999997 Q 1.157,2.4699999999999998 0.927,2.4699999999999998 "
        "Q 0.732,2.4699999999999998 0.604,2.372 Q 0.477,2.275 0.477,2.105 Q 0.477,2.02 0.517,1.962 "
        "Q 0.557,1.9049999999999998 0.599,1.8699999999999999 Q 0.642,1.835 0.642,1.83 "
        "Q 0.642,1.795 0.574,1.7449999999999999 Q 0.507,1.6949999999999998 0.412,1.6949999999999998 "
        "Q 0.257,1.6949999999999998 0.164,1.7919999999999998 Q 0.072,1.89 0.072,2.04 "
        "Q 0.072,2.2399999999999998 0.207,2.38 Q 0.342,2.52 0.549,2.585 Q 0.757,2.65 0.972,2.65 "
        "Q 1.347,2.65 1.619,2.465 Q 1.892,2.28 1.892,1.9 Q 1.892,1.625 1.742,1.4 "
        "Q 1.592,1.1749999999999998 1.384,1.017 Q 1.177,0.8599999999999999 0.842,0.645 "
        "Q 0.577,0.48 0.447,0.3799999999999999 Z"
    ),
    "three": parse_path(
        "M 0.9,1.336 L 0.715,1.336 Q 0.68,1.336 0.66,1.366 Q 0.64,1.396 0.64,1.436 "
        "Q 0.64,1.481 0.66,1.513 Q 0.68,1.546 0.715,1.551 L 0.9,1.551 Q 1.095,1.571 1.213,1.726 "
        "Q 1.33,1.881 1.33,2.101 Q 1.33,2.341 1.195,2.468 Q 1.06,2.596 0.88,2.596 "
        "Q 0.71,2.596 0.588,2.498 Q 0.465,2.401 0.465,2.231 Q 0.465,2.121 0.508,2.083 "
        "Q 0.55,2.0460000000000003 0.59,2.0380000000000003 Q 0.63,2.031 0.63,2.026 "
        "Q 0.63,1.991 0.563,1.941 Q 0.495,1.891 0.4,1.891 Q 0.24,1.891 0.15,1.991 "
        "Q 0.06,2.091 0.06,2.246 Q 0.06,2.491 0.29,2.626 Q 0.52,2.761 0.885,2.761 "
        "Q 1.275,2.761 1.53,2.591 Q 1.785,2.421 1.785,2.101 Q 1.785,1.891 1.638,1.711 "
        "Q 1.49,1.531 1.215,1.456 L 1.215,1.436 Q 1.495,1.406 1.7,1.258 "
        "Q 1.905,1.111 1.905,0.791 Q 1.905,0.386 1.61,0.193 Q 1.315,0.001 0.87,0.001 "
        "Q 0.505,0.0009999999999998899 0.253,0.1429999999999998 Q 0.0,0.286 0.0,0.5609999999999999 "
        "Q 0.0,0.706 0.09,0.8109999999999999 Q 0.18,0.9159999999999999 0.34,0.9159999999999999 "
        "Q 0.435,0.9159999999999999 0.503,0.8660000000000001 Q 0.57,0.8160000000000001 0.57,0.7809999999999999 "
        "Q 0.57,0.776 0.525,0.7429999999999999 Q 0.48,0.7109999999999999 0.443,0.6560000000000001 "
        "Q 0.405,0.601 0.405,0.516 Q 0.405,0.3610000000000002 0.538,0.27300000000000013 "
        "Q 0.67,0.18599999999999994 0.885,0.18599999999999994 Q 1.42,0.18599999999999994 1.42,0.7809999999999999 "
        "Q 1.42,1.026 1.29,1.173 Q 1.16,1.321 0.9,1.336 Z"
    ),
    "four": parse_path(
        "M 1.355,0.09599999999999964 L 1.355,0.8609999999999998 L 0.16,0.8609999999999998 "
        "Q 0.08,0.8609999999999998 0.04,0.9109999999999998 Q 0.0,0.9609999999999999 0.0,1.0359999999999998 "
        "Q 0.0,1.1009999999999998 0.035,1.1459999999999997 L 1.44,2.6809999999999996 "
        "Q 1.49,2.731 1.595,2.731 Q 1.675,2.731 1.73,2.6889999999999996 Q 1.785,2.646 1.79,2.5559999999999996 "
        "L 1.79,1.1059999999999999 L 2.09,1.1059999999999999 Q 2.16,1.1059999999999999 2.19,1.0889999999999997 "
        "Q 2.22,1.0709999999999997 2.225,0.9859999999999998 Q 2.225,0.9309999999999998 2.203,0.8959999999999997 "
        "Q 2.18,0.8609999999999998 2.13,0.8609999999999998 L 1.79,0.8609999999999998 L 1.79,0.09599999999999964 "
        "Q 1.79,0.05099999999999971 1.725,0.0259999999999998 Q 1.66,0.0009999999999998899 1.575,0.0009999999999998899 "
        "Q 1.49,0.0009999999999998899 1.425,0.0259999999999998 Q 1.36,0.05099999999999971 1.355,0.09599999999999964 "
        "M 1.355,2.291 L 0.29,1.1059999999999999 L 1.355,1.1059999999999999 L 1.355,2.291 Z"
    ),
    "five": parse_path(
        "M 0.135,1.4500000000000002 L 0.14,1.5100000000000002 L 0.295,2.7 L 1.67,2.7 "
        "Q 1.74,2.7 1.783,2.6550000000000002 Q 1.825,2.6100000000000003 1.825,2.5300000000000002 "
        "Q 1.825,2.345 1.635,2.345 L 0.525,2.345 L 0.42,1.6500000000000001 "
        "Q 0.64,1.7850000000000001 0.96,1.7850000000000001 Q 1.175,1.7850000000000001 1.393,1.6900000000000002 "
        "Q 1.61,1.5950000000000002 1.755,1.4000000000000001 Q 1.9,1.205 1.9,0.9150000000000003 "
        "Q 1.9,0.625 1.758,0.41700000000000026 Q 1.615,0.20999999999999996 1.378,0.10499999999999998 "
        "Q 1.14,0.0 0.86,0.0 Q 0.49,0.0 0.245,0.13500000000000023 Q 0.0,0.27 0.0,0.5550000000000002 "
        "Q 0.0,0.7100000000000002 0.093,0.8270000000000002 Q 0.185,0.9450000000000003 0.34,0.9450000000000003 "
        "Q 0.435,0.9450000000000003 0.503,0.8950000000000002 Q 0.57,0.8450000000000002 0.57,0.8100000000000003 "
        "Q 0.57,0.8050000000000002 0.525,0.7650000000000001 Q 0.48,0.7250000000000001 0.443,0.6670000000000003 "
        "Q 0.405,0.6100000000000003 0.405,0.5350000000000001 Q 0.405,0.3650000000000002 0.528,0.27500000000000036 "
        "Q 0.65,0.18500000000000005 0.87,0.18500000000000005 Q 1.145,0.18500000000000005 1.283,0.38000000000000034 "
        "Q 1.42,0.5750000000000002 1.42,0.8900000000000001 Q 1.42,1.1800000000000002 1.28,1.372 "
        "Q 1.14,1.5650000000000002 0.845,1.5650000000000002 Q 0.71,1.5650000000000002 0.613,1.5220000000000002 "
        "Q 0.515,1.4800000000000002 0.405,1.4000000000000001 Q 0.34,1.3550000000000002 0.298,1.332 "
        "Q 0.255,1.3100000000000003 0.215,1.3100000000000003 Q 0.135,1.3100000000000003 0.135,1.45 Z"
    ),
}


def _make_field_lines_markers(vertical_field=False):
    width_line_generator = make_vline if not vertical_field else make_hline
    length_line_generator = make_hline if not vertical_field else make_vline
    # First, make the field border:
    field_kwargs = {"line_width": 5, "line_color": "white", "layer": "below"}
    field_border = [
        length_line_generator(0, FIELD_LENGTH, 0, **field_kwargs),
        length_line_generator(0, FIELD_LENGTH, FIELD_WIDTH, **field_kwargs),
        width_line_generator(0, FIELD_WIDTH, 0, **field_kwargs),
        width_line_generator(0, FIELD_WIDTH, FIELD_LENGTH, **field_kwargs),
    ]

    # Now make the yard and hash lines:
    line_kwargs = {"line_width": 2, "line_color": "white", "layer": "below"}
    five_yard_lines = [width_line_generator(0, FIELD_WIDTH, 5 * i, **line_kwargs) for i in range(2, 23)]
    hash_width = 2 / 3  # Hashes are 2/3rds of a yard
    hash_length = 6 + 6 / 36  # six yards, six inches
    one_yard_lines = [
        width_line_generator(w, w + hash_width, i, **line_kwargs)
        for i in range(10, 111)
        if i % 10 != 0
        for w in [1, 23.58333, 23.58333 + hash_length - hash_width, 52.3 - hash_width]
    ]

    field_lines = field_border + five_yard_lines + one_yard_lines

    number_kwargs = {"line_color": "white", "fillcolor": "white", "layer": "below"}
    number_length_location_mapping = {
        20: FIELD_NUMBER_PATHS["one"],
        30: FIELD_NUMBER_PATHS["two"],
        40: FIELD_NUMBER_PATHS["three"],
        50: FIELD_NUMBER_PATHS["four"],
        60: FIELD_NUMBER_PATHS["five"],
        70: FIELD_NUMBER_PATHS["four"],
        80: FIELD_NUMBER_PATHS["three"],
        90: FIELD_NUMBER_PATHS["two"],
        100: FIELD_NUMBER_PATHS["one"],
    }
    number_length_offsets = [-2.7, 0.5] if not vertical_field else [-3.2, 0.5]
    zero_length_offsets = [0.5, -2.4] if not vertical_field else [0.4, -2.9]
    width_offsets = [4, 47] if not vertical_field else [47, 4]
    rotations = [0, 180] if not vertical_field else [90, 270]
    field_numbers = []

    for length_location, number in number_length_location_mapping.items():
        number_offsets = [
            complex(length_location + length_offset, width_offset)
            if not vertical_field
            else complex(width_offset, length_location + length_offset)
            for length_offset, width_offset in zip(number_length_offsets, width_offsets)
        ]
        zero_offsets = [
            complex(length_location + length_offset, width_offset)
            if not vertical_field
            else complex(width_offset, length_location + length_offset)
            for length_offset, width_offset in zip(zero_length_offsets, width_offsets)
        ]
        field_numbers += [
            dict(
                type="path",
                path=number.rotated(rotation, get_path_midpoint(number)).translated(offset).d(),
                **number_kwargs
            )
            for rotation, offset in zip(rotations, number_offsets)
        ]
        field_numbers += [
            dict(
                type="path",
                path=FIELD_NUMBER_PATHS["zero"].rotated(rotation, get_path_midpoint(number)).translated(offset).d(),
                **number_kwargs
            )
            for rotation, offset in zip(rotations, zero_offsets)
        ]

    # TODO: Figure out why arrow offsets are screwy when using a vertical field.
    arrow = parse_path("M 0.4 -0.20 L -0.4 0 L 0.4 0.20 L 0.4 -0.20 Z")
    arrow_length_offsets = (
        [16.5, 26.5, 36.5, 46.5, 73.8, 83.8, 93.8, 103.8]
        if not vertical_field
        else [16.1, 26.1, 36.1, 46.1, 73.8, 83.8, 93.8, 103.8]
    )
    arrow_rotations = [0, 0, 0, 0, 180, 180, 180, 180]
    arrow_width_offsets = [5.2] * len(arrow_length_offsets)
    arrow_length_offsets += [FIELD_LENGTH - offset for offset in arrow_length_offsets]
    arrow_rotations += arrow_rotations[::-1]
    arrow_width_offsets += ([48.5] if not vertical_field else [48.1]) * len(arrow_width_offsets)
    field_indicators = [
        dict(
            type="path",
            path=arrow.rotated(rotation, 0).translated(complex(length_offset, width_offset)).d(),
            **number_kwargs
        )
        if not vertical_field
        else dict(
            type="path",
            path=arrow.rotated(rotation + 90, 0).translated(complex(width_offset, length_offset)).d(),
            **number_kwargs
        )
        for length_offset, rotation, width_offset in zip(arrow_length_offsets, arrow_rotations, arrow_width_offsets)
    ]

    return field_lines + field_numbers + field_indicators


FIELD = Field(FIELD_LENGTH, FIELD_WIDTH, _make_field_lines_markers(), BACKGROUND_COLOR)
VERTICAL_FIELD = Field(FIELD_WIDTH, FIELD_LENGTH, _make_field_lines_markers(vertical_field=True), BACKGROUND_COLOR)
