from __future__ import annotations

import math

from .core import Layer

from typing import Optional


class Facet(Layer):
    def __init__(
            self, facet_mapping: str,
            num_col: Optional[int] = None, num_row: Optional[int] = None
    ):
        self.facet_mapping = facet_mapping
        self.num_col = num_col
        self.num_row = num_row
        if self.num_row is not None and self.num_col is not None:
            raise ValueError("Can only specify one of num_col or num_row")

    def get_mappings(self):
        return [self.facet_mapping]

    def faceting(self, data):
        groups = data.groupby(self.facet_mapping)
        if self.num_col is not None:
            self.num_row = math.ceil(len(groups) / self.num_col)
        elif self.num_row is not None:
            self.num_col = math.ceil(len(groups) / self.num_row)
        else:
            self.num_row = len(groups)
            self.num_col = 1
        return groups
