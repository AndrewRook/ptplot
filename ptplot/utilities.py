import dask.dataframe as dd
import numpy as np
import warnings

from typing import Sequence, Union


class DaskCompatibilityWarning(UserWarning):
    """
    A warning for cases where some noncritical functionality
    is skipped because it does not work in dask. For example,
    skipping error checking that works for pandas but would
    require running ``.compute()`` for dask, instead this will
    raise a warning explaining that the user needs to be
    responsible for that checking themselves.
    """

    pass


def warn_if_dask(input_dataframe):
    if type(input_dataframe) == dd.DataFrame:
        warnings.warn(
            "Error checking suppressed with dask dataframes to prevent " "unnecessary compute calls",
            DaskCompatibilityWarning,
        )


def get_path_midpoint(path):
    min_x, max_x, min_y, max_y = path.bbox()
    midpoint_x = (max_x + min_x) / 2
    midpoint_y = (max_y + min_y) / 2
    return complex(midpoint_x, midpoint_y)


def make_vline(y0, y1, x, **kwargs):
    """Make a vertical line of a defined distance."""
    return dict(type="line", y0=y0, y1=y1, x0=x, x1=x, **kwargs)


def make_hline(x0, x1, y, **kwargs):
    """Make a horizontal line of a defined distance."""
    return dict(type="line", y0=y, y1=y, x0=x0, x1=x1, **kwargs)


def generate_time_elapsed_labels(time_zeropoint, time_column_name, formatting="{: .2f} s"):
    """Create a function that can be used in plotting animations to show time elapsed compared
    to a user-defined zeropoint.
    """

    def time_elapsed_function(frame_data):
        frame_times = frame_data[time_column_name]
        max_frame_time = frame_times.max()
        min_frame_time = frame_times.min()
        if max_frame_time != min_frame_time:
            raise ValueError(f"Frame has multiple times: {min_frame_time}, {max_frame_time}")
        time_elapsed = (max_frame_time - time_zeropoint) / np.timedelta64(1, "s")
        return formatting.format(time_elapsed)

    return time_elapsed_function


def generate_labels_from_multiple_columns(
    columns: Sequence[str],
    column_formatting: Union[Sequence[str], None] = None,
    separator: str = " ",
    na_rep: Union[str, None] = None,
):
    if column_formatting is not None and len(columns) != len(column_formatting):
        raise IndexError("If column_formatting is used, must have the same length as columns")
    if column_formatting is None:
        column_formatting = [None] * len(columns)

    def column_concat_function(data):
        string_columns = [
            data[column].astype(str) if formatter is None else data[column].map(formatter.format)
            for column, formatter in zip(columns, column_formatting)
        ]
        # TODO: functools.reduce on the str.cat function
