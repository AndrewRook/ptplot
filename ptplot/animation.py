from ptplot.core import Layer

from typing import Sequence

class Animation(Layer):
    def __init__(self, frame_mapping: str):
        self.frame_mapping = frame_mapping

    def get_mappings(self) -> Sequence[str]:
        return [self.frame_mapping]
