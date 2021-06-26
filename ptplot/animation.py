from ptplot.core import Layer


class Animation(Layer):
    def __init__(self, frame_mapping):
        self.frame_mapping = frame_mapping

    def get_mappings(self):
        return [self.frame_mapping]
