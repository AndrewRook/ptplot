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
