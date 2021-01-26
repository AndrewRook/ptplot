import dask.dataframe as dd
import pandas as pd
from typing import Union


def get_data_between_events(
        play_data: Union[pd.DataFrame, dd.DataFrame],
        start_event: Union[str, int],
        end_event: Union[str, int],
        event_column: Union[str, pd.Series, dd.Series],
        timestamp_column: Union[str, pd.Series, dd.Series]):
    """
    Filter a dataframe to only have data between two events

    Parameters
    ----------
    play_data
    start_event
    end_event
    event_column
    timestamp_column

    Returns
    -------

    """
    if type(event_column) in [pd.Series, dd.Series]:
        if len(event_column) != len(play_data):
            raise ValueError(
                f"Lengths must match! event_column has length {len(event_column)} but "
                f"play_data has length {len(play_data)}"
            )
    else:
        event_column = play_data[event_column]

    if type(timestamp_column) in [pd.Series, dd.Series]:
        if len(timestamp_column) != len(play_data):
            raise ValueError(
                f"Lengths must match! timestamp_column has length {len(timestamp_column)} but "
                f"play_data has length {len(play_data)}"
            )
    else:
        timestamp_column = play_data[timestamp_column]

    start_time = timestamp_column[event_column == start_event].unique()

    if len(start_time) != 1:
        raise ValueError(
            f"{start_event} appeared in the data at {len(start_time)} timestamps! Must appear exactly once!"
        )
    start_time = start_time[0]

    end_time = timestamp_column[event_column == end_event].unique()
    if len(end_time) != 1:
        raise ValueError(
            f"{end_event} appeared in the play data at {len(end_time)} timestamps! Must appear exactly once!"
        )
    end_time = end_time[0]

    if end_time <= start_time:
        raise ValueError(
            f"End time {end_time} does not occur after start time {start_time}!"
        )

    good_data = play_data[timestamp_column.between(start_time, end_time)].copy(deep=True)

    return good_data
