import dask.dataframe as dd
import pandas as pd
import warnings
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
    #breakpoint()
    # Just taking the zeroth index doesn't work with dask, so we iterate over the
    # (hopefully very small) array and take the max instead:
    start_time = start_time.max()

    end_time = timestamp_column[event_column == end_event].unique()
    if len(end_time) != 1:
        raise ValueError(
            f"{end_event} appeared in the data at {len(end_time)} timestamps! Must appear exactly once!"
        )
    end_time = end_time.max()

    good_data = play_data[timestamp_column.between(start_time, end_time)].copy()

    if len(good_data) == 0:
        raise ValueError(
            "No records identified! Check to make sure that your events are in the proper order and "
            "appear in the data"
        )

    return good_data.reset_index(drop=True)
