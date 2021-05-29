from __future__ import annotations

import math
import matplotlib.pyplot as plt
import numpy as np

from .layer import Layer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ptplot import PTPlot


class Field(Layer):
    def __init__(
            self, vertical_orientation: bool = False,
            min_yards: float = -13,
            max_yards: float = 113,
            relative_yardlines: bool = False,
            sideline_buffer: float = 3,
            pixels_per_yard: int = 20):
        self.vertical_orientation = vertical_orientation
        self.min_yards = min_yards
        self.max_yards = max_yards
        self.relative_yardlines = relative_yardlines
        self.sideline_buffer = sideline_buffer
        self.pixels_per_yard = pixels_per_yard


    def __radd__(self, ptplot: PTPlot):

        field_width_yards = 53.3
        y_min = 0 - self.sideline_buffer
        y_max = field_width_yards + self.sideline_buffer
        x_yards = self.max_yards - self.min_yards
        y_yards = y_max - y_min

        fig, ax = plt.subplots(
            figsize=(x_yards, y_yards), dpi=self.pixels_per_yard,
            tight_layout={"pad": 0}
        )
        ax.set_facecolor("green")
        ax.set_axis_off()
        ax.add_artist(ax.patch)
        ax.patch.set_zorder(-1)
        ax.set_xlim(self.min_yards, self.max_yards)
        ax.set_ylim(y_min, y_max)

        vlines = [
            yard
            for yard in range(
                max(math.ceil(self.min_yards), 0),
                min(math.floor(self.max_yards), 100) + 1
            )
            if yard % 5 == 0
        ]
        endzone_vlines = [
            yard
            for yard in [-10, 110]
            if yard > self.min_yards and yard < self.max_yards
        ]

        ax.vlines(vlines, 0, field_width_yards, color="white", lw=self.pixels_per_yard)
        ax.vlines(endzone_vlines, 0, field_width_yards, color="white", lw=(2 * self.pixels_per_yard))

        if self.sideline_buffer > 0:
            ax.hlines(
                [0, field_width_yards], max(-10.2, self.min_yards), min(110.2, self.max_yards),
                color="white", lw=(2 * self.pixels_per_yard)
            )

        fig.canvas.draw()
        field = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        field = field.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close(fig)
        img = np.empty(field.shape[:2], dtype=np.uint32)
        field_view = img.view(dtype=np.uint8).reshape((field.shape[0], field.shape[1], 4))
        field_view[:, :, 0] = field[:, :, 0]
        field_view[:, :, 1] = field[:, :, 1]
        field_view[:, :, 2] = field[:, :, 2]
        field_view[:, :, 3] = 200

        ptplot.figure.image_rgba(image=[img], x=self.min_yards, y=y_min, dw=x_yards, dh=y_yards)