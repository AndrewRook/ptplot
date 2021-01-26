import dask.dataframe as dd
import functools
import pandas as pd
import pytest


DASK_CONSTRUCTOR = functools.partial(dd.from_pandas, npartitions=2)


def pytest_generate_tests(metafunc):
    if "data_constructor" in metafunc.fixturenames:
        metafunc.parametrize(
            "data_constructor",
            [
                pytest.param(lambda x: x, id="pandas"),  # empty passthrough
                pytest.param(DASK_CONSTRUCTOR, id="dask")
            ]
        )
