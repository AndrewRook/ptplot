import dask
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


    @pytest.mark.parametrize("start_event, end_event", ([0, 1], [1, 0]))
    def test_event_at_multiple_times_raises_error(self, start_event, end_event, data_constructor):
        data = data_constructor(pd.DataFrame({
            "event": [0, 0, 1, 1, 0],
            "timestamp": pd.to_datetime([
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:03Z"
            ])
        }))

        with pytest.raises(ValueError, match="0 appeared in the data at 2 timestamps!"):
            ft.get_data_between_events(data, start_event, end_event, "event", "timestamp")

    def test_event_end_after_event_start_raises_error(self, data_constructor):
        data = data_constructor(pd.DataFrame({
            "event": [0, 0, 1, 1],
            "timestamp": pd.to_datetime([
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:02Z"
            ])
        }))

        with pytest.raises(ValueError, match="No records identified!"):
            ft.get_data_between_events(data, 1, 0, "event", "timestamp")

    def test_works_single_dataframe(self, data_constructor):
        data = data_constructor(pd.DataFrame({
            "event": [0, 0, 1, 1, 2, 2, 3],
            "timestamp": pd.to_datetime([
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:03Z",
                "2000-01-01T00:00:03Z",
                "2000-01-01T00:00:04Z"
            ])
        }))

        expected_result = pd.DataFrame({
            "event": [1, 1, 2, 2],
            "timestamp": pd.to_datetime([
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:03Z",
                "2000-01-01T00:00:03Z",
            ])
        })

        actual_result = (dask.compute(
            ft.get_data_between_events(data, 1, 2, "event", "timestamp")
        )[0]).reset_index(drop=True)
        pd.testing.assert_frame_equal(expected_result, actual_result)

    def test_works_with_dataframe_plus_series(self, data_constructor):
        data = data_constructor(pd.DataFrame({
            "thing": [1, 2, 3, 4, 5, 6, 7]
        }))
        event = data_constructor(pd.Series([0, 0, 1, 1, 2, 2, 3]))
        timestamp = data_constructor(pd.Series(pd.to_datetime([
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:03Z",
                "2000-01-01T00:00:03Z",
                "2000-01-01T00:00:04Z"
        ])))

        expected_result = pd.DataFrame({
            "thing": [3, 4, 5, 6]
        })

        actual_result = (dask.compute(
            ft.get_data_between_events(data, 1, 2, event, timestamp)
        )[0]).reset_index(drop=True)
        pd.testing.assert_frame_equal(expected_result, actual_result)
