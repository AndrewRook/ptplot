import dask
import pandas as pd
import pytest

from player_tracking import filtering as ft


class TestGetDataBetweenEvents:

    @pytest.mark.parametrize("start_event, end_event", ([0, 1], [1, 0]))
    def test_event_at_multiple_times_raises_error(self, start_event, end_event):
        data = pd.DataFrame({
            "event": [0, 0, 1, 1, 0],
            "timestamp": pd.to_datetime([
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:03Z"
            ])
        })

        with pytest.raises(ValueError, match="0 appeared in the data at 2 timestamps!"):
            ft.get_data_between_events(data, start_event, end_event, "event", "timestamp")

    def test_event_end_after_event_start_raises_error(self):
        data = pd.DataFrame({
            "event": [0, 0, 1, 1],
            "timestamp": pd.to_datetime([
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:01Z",
                "2000-01-01T00:00:02Z",
                "2000-01-01T00:00:02Z"
            ])
        })

        with pytest.raises(ValueError, match="No records identified!"):
            ft.get_data_between_events(data, 1, 0, "event", "timestamp")

    def test_works(self, data_constructor):
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

