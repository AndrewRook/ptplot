import dask.dataframe as dd
import pandas as pd

from typing import Union


class TrackingFrame:

    def __init__(
            self,
            dataframe: Union[dd.DataFrame, pd.DataFrame],
            timestamp_column: str,
            event_column: Union[str, None] = None
    ):
        self._dataframe = dataframe
        self.timestamp_column = timestamp_column
        self.event_column = event_column

    @property
    def dataframe_type(self):
        """The type of the underlying dataframe. Useful for situations
        where the implementation differs between pandas and dask
        """
        return type(self._dataframe)

    def __getattr__(self, item):
        """
        Passes anything that isn't defined in the class to the dataframe
        """
        return getattr(self._dataframe, item)

    # These dunder methods aren't passed properly to __getattr__,
    # so I have to pass them explicitly
    def __getitem__(self, name):
        return self._dataframe.__getitem__(name)

    def __setitem__(self, key, value):
        return self._dataframe.__setitem__(key, value)

    def __delitem__(self, key):
        return self.__dataframe.__delitem__(key)