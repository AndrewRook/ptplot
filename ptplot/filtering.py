import dask.dataframe as dd
import pandas as pd

from typing import Union

from .utils import warn_if_dask


def get_data_between_events(
        play_data: Union[pd.DataFrame, dd.DataFrame],
        start_event: Union[str, int],
        end_event: Union[str, int],
        event_column: str,
        timestamp_column: str):
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
    warn_if_dask(play_data)

    event_data= play_data[event_column]

    timestamp_data = play_data[timestamp_column]

    start_time = timestamp_data[event_data == start_event].unique()

    if type(play_data) == pd.DataFrame:
        if len(start_time) != 1:
            raise ValueError(
                f"{start_event} appeared in the data at {len(start_time)} timestamps! Must appear exactly once!"
            )
    # Just taking the zeroth index doesn't work with dask, so we iterate over the
    # (hopefully very small) array and take the max instead:
    start_time = start_time.max()

    end_time = timestamp_data[event_data == end_event].unique()

    if type(play_data) == pd.DataFrame:
        if len(end_time) != 1:
            raise ValueError(
                f"{end_event} appeared in the data at {len(end_time)} timestamps! Must appear exactly once!"
            )
    end_time = end_time.max()

    good_data = play_data[timestamp_data.between(start_time, end_time)].copy()

    if type(play_data) == pd.DataFrame:
        if len(good_data) == 0:
            raise ValueError(
                "No records identified! Check to make sure that your events are in the proper order and "
                "appear in the data"
            )

    return good_data.reset_index(drop=True)
