import dask.dataframe as dd
import pandas as pd
import pytest

from player_tracking import filtering as ft


class TestGetDataBetweenEvents:

    def test_event_column_has_wrong_length(self, data_constructor):
        data = data_constructor(pd.DataFrame({"one": [1, 2, 3]}))
        event = data_constructor(pd.Series([1, 2, 3, 4]))
        timestamp = data_constructor(pd.Series([1, 2, 3]))
        with pytest.raises(ValueError, match="event_column has length 4 but play_data has length 3"):
            ft.get_data_between_events(data, 1, 3, event, timestamp)

    def test_timestamp_column_has_wrong_length(self, data_constructor):
        data = data_constructor(pd.DataFrame({"one": [1, 2, 3]}))
        event = data_constructor(pd.Series([1, 2, 3]))
        timestamp = data_constructor(pd.Series([1, 2, 3, 4]))
        with pytest.raises(ValueError, match="timestamp_column has length 4 but play_data has length 3"):
            ft.get_data_between_events(data, 1, 3, event, timestamp)

