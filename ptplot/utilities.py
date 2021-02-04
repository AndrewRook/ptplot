import dask.dataframe as dd
import warnings


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
            "Error checking suppressed with dask dataframes to prevent "
            "unnecessary compute calls",
            DaskCompatibilityWarning
        )


def get_path_midpoint(path):
    min_x, max_x, min_y, max_y = path.bbox()
    midpoint_x = (max_x + min_x) / 2
    midpoint_y = (max_y + min_y) / 2
    return complex(midpoint_x, midpoint_y)


def make_vline(y0, y1, x, **kwargs):
    """Make a vertical line of a defined distance."""
    return dict(
        type="line",
        y0=y0, y1=y1,
        x0=x, x1=x,
        **kwargs
    )


def make_hline(x0, x1, y, **kwargs):
    """Make a horizontal line of a defined distance."""
    return dict(
        type="line",
        y0=y, y1=y,
        x0=x0, x1=x1,
        **kwargs
    )