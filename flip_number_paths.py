from copy import deepcopy
from svgpathtools import parse_path, Path, Line, Arc, QuadraticBezier

# These numbers came from a text to svg converter
# (Alice font, https://danmarshall.github.io/google-font-to-svg-path/)
# That was designed for SVGs where 0 is the upper left instead of the bottom left.
# This script just flips them - I couldn't use Path.scaled() because some of the
# paths are Arcs which are unsupported.
upside_down_one = parse_path(
    "M 0.713 2.01 L 0.713 0.97 A 3.257 3.257 0 0 0 0.714 0.901 A 1.126 1.126 0 0 0 0.691 0.633 "
    "Q 0.663 0.53 0.593 0.5 Q 0.523 0.47 0.363 0.47 L 0.118 0.47 A 0.095 0.095 0 0 1 0.028 0.35 "
    "Q 0.033 0.275 0.058 0.258 Q 0.083 0.24 0.121 0.24 L 0.173 0.24 Q 0.383 0.24 0.583 0.173 "
    "Q 0.783 0.105 1.018 0.01 Q 1.048 0 1.068 0 Q 1.148 0 1.148 0.115 L 1.148 2.01 "
    "Q 1.148 2.23 1.201 2.325 Q 1.253 2.42 1.366 2.445 Q 1.478 2.47 1.728 2.47 L 1.778 2.47 "
    "Q 1.818 2.47 1.836 2.49 Q 1.853 2.51 1.858 2.57 Q 1.858 2.69 1.768 2.69 "
    "Q 1.408 2.675 0.928 2.675 Q 0.453 2.675 0.093 2.69 A 0.095 0.095 0 0 1 0.003 2.57 "
    "Q 0.008 2.51 0.026 2.49 Q 0.043 2.47 0.083 2.47 Q 0.363 2.47 0.481 2.448 "
    "Q 0.598 2.425 0.656 2.33 Q 0.713 2.235 0.713 2.01 Z"
)
upside_down_two = parse_path(
    "M 0.447 2.27 L 0.447 2.295 L 1.787 2.295 A 0.449 0.449 0 0 1 1.969 2.323 "
    "Q 2.027 2.35 2.027 2.47 Q 2.027 2.65 1.852 2.65 L 0.177 2.65 Q 0.002 2.65 0.002 2.47 "
    "Q 0.007 2.365 0.059 2.3 Q 0.112 2.235 0.232 2.155 Q 0.627 1.89 0.844 1.718 "
    "Q 1.062 1.545 1.237 1.28 Q 1.412 1.015 1.412 0.685 Q 1.412 0.445 1.284 0.313 "
    "Q 1.157 0.18 0.927 0.18 Q 0.732 0.18 0.604 0.278 Q 0.477 0.375 0.477 0.545 "
    "Q 0.477 0.63 0.517 0.688 Q 0.557 0.745 0.599 0.78 Q 0.642 0.815 0.642 0.82 "
    "Q 0.642 0.855 0.574 0.905 Q 0.507 0.955 0.412 0.955 Q 0.257 0.955 0.164 0.858 "
    "Q 0.072 0.76 0.072 0.61 Q 0.072 0.41 0.207 0.27 Q 0.342 0.13 0.549 0.065 "
    "Q 0.757 0 0.972 0 Q 1.347 0 1.619 0.185 Q 1.892 0.37 1.892 0.75 Q 1.892 1.025 1.742 1.25 "
    "Q 1.592 1.475 1.384 1.633 Q 1.177 1.79 0.842 2.005 Q 0.577 2.17 0.447 2.27 Z"
)
upside_down_three = parse_path(
    "M 0.9 1.426 L 0.715 1.426 Q 0.68 1.426 0.66 1.396 Q 0.64 1.366 0.64 1.326 "
    "Q 0.64 1.281 0.66 1.249 Q 0.68 1.216 0.715 1.211 L 0.9 1.211 Q 1.095 1.191 1.213 1.036 "
    "Q 1.33 0.881 1.33 0.661 Q 1.33 0.421 1.195 0.294 Q 1.06 0.166 0.88 0.166 "
    "Q 0.71 0.166 0.588 0.264 Q 0.465 0.361 0.465 0.531 Q 0.465 0.641 0.508 0.679 "
    "Q 0.55 0.716 0.59 0.724 Q 0.63 0.731 0.63 0.736 Q 0.63 0.771 0.563 0.821 "
    "Q 0.495 0.871 0.4 0.871 Q 0.24 0.871 0.15 0.771 Q 0.06 0.671 0.06 0.516 "
    "Q 0.06 0.271 0.29 0.136 Q 0.52 0.001 0.885 0.001 Q 1.275 0.001 1.53 0.171 "
    "Q 1.785 0.341 1.785 0.661 Q 1.785 0.871 1.638 1.051 Q 1.49 1.231 1.215 1.306 "
    "L 1.215 1.326 Q 1.495 1.356 1.7 1.504 Q 1.905 1.651 1.905 1.971 Q 1.905 2.376 1.61 2.569 "
    "Q 1.315 2.761 0.87 2.761 Q 0.505 2.761 0.253 2.619 Q 0 2.476 0 2.201 Q 0 2.056 0.09 1.951 "
    "Q 0.18 1.846 0.34 1.846 Q 0.435 1.846 0.503 1.896 Q 0.57 1.946 0.57 1.981 "
    "Q 0.57 1.986 0.525 2.019 Q 0.48 2.051 0.443 2.106 Q 0.405 2.161 0.405 2.246 "
    "Q 0.405 2.401 0.538 2.489 Q 0.67 2.576 0.885 2.576 Q 1.42 2.576 1.42 1.981 "
    "Q 1.42 1.736 1.29 1.589 Q 1.16 1.441 0.9 1.426 Z"
)
upside_down_four = parse_path(
    "M 1.355 2.636 L 1.355 1.871 L 0.16 1.871 Q 0.08 1.871 0.04 1.821 Q 0 1.771 0 1.696 "
    "Q 0 1.631 0.035 1.586 L 1.44 0.051 Q 1.49 0.001 1.595 0.001 Q 1.675 0.001 1.73 0.043 "
    "Q 1.785 0.086 1.79 0.176 L 1.79 1.626 L 2.09 1.626 Q 2.16 1.626 2.19 1.643 "
    "Q 2.22 1.661 2.225 1.746 Q 2.225 1.801 2.203 1.836 Q 2.18 1.871 2.13 1.871 "
    "L 1.79 1.871 L 1.79 2.636 Q 1.79 2.681 1.725 2.706 Q 1.66 2.731 1.575 2.731 "
    "Q 1.49 2.731 1.425 2.706 Q 1.36 2.681 1.355 2.636 Z M 1.355 0.441 L 0.29 1.626 "
    "L 1.355 1.626 L 1.355 0.441 Z"
)
upside_down_five = parse_path(
    "M 0.135 1.25 L 0.14 1.19 L 0.295 0 L 1.67 0 Q 1.74 0 1.783 0.045 Q 1.825 0.09 1.825 0.17 "
    "Q 1.825 0.355 1.635 0.355 L 0.525 0.355 L 0.42 1.05 Q 0.64 0.915 0.96 0.915 "
    "Q 1.175 0.915 1.393 1.01 Q 1.61 1.105 1.755 1.3 Q 1.9 1.495 1.9 1.785 Q 1.9 2.075 1.758 2.283 "
    "Q 1.615 2.49 1.378 2.595 Q 1.14 2.7 0.86 2.7 Q 0.49 2.7 0.245 2.565 Q 0 2.43 0 2.145 "
    "Q 0 1.99 0.093 1.873 Q 0.185 1.755 0.34 1.755 Q 0.435 1.755 0.503 1.805 Q 0.57 1.855 0.57 1.89 "
    "Q 0.57 1.895 0.525 1.935 Q 0.48 1.975 0.443 2.033 Q 0.405 2.09 0.405 2.165 "
    "Q 0.405 2.335 0.528 2.425 Q 0.65 2.515 0.87 2.515 Q 1.145 2.515 1.283 2.32 "
    "Q 1.42 2.125 1.42 1.81 Q 1.42 1.52 1.28 1.328 Q 1.14 1.135 0.845 1.135 "
    "Q 0.71 1.135 0.613 1.178 Q 0.515 1.22 0.405 1.3 Q 0.34 1.345 0.298 1.368 "
    "Q 0.255 1.39 0.215 1.39 Q 0.135 1.39 0.135 1.25 Z"
)


def flip_path(upside_down_path):
    path = []#deepcopy(upside_down_path)
    _, _, min_y, max_y = upside_down_path.bbox()
    offset = max_y + min_y
    for segment in upside_down_path._segments:
        if type(segment) is Line:
            path.append(Line(
                complex(segment.start.real, -segment.start.imag + offset),
                complex(segment.end.real, -segment.end.imag + offset)

            ))
        elif type(segment) is Arc:
            path.append(Arc(
                complex(segment.start.real, -segment.start.imag + offset),
                segment.radius,
                abs(180 - segment.rotation),
                segment.large_arc,
                not segment.sweep,
                complex(segment.end.real, -segment.end.imag + offset)
            ))
        elif type(segment) is QuadraticBezier:
            path.append(QuadraticBezier(
                complex(segment.start.real, -segment.start.imag + offset),
                complex(segment.control.real, -segment.control.imag + offset),
                complex(segment.end.real, -segment.end.imag + offset)

            ))
        else:
            raise ValueError(f"Unknown type: {type(segment)}")

    return Path(*path)


if __name__ == "__main__":
    print("one")
    print(flip_path(upside_down_one).d())
    print("\ntwo")
    print(flip_path(upside_down_two).d())
    print("\nthree")
    print(flip_path(upside_down_three).d())
    print("\nfour")
    print(flip_path(upside_down_four).d())
    print("\nfive")
    print(flip_path(upside_down_five).d())

