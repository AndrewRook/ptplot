import pandas as pd
import pytest

from ptplot import utilities


class TestGenerateTimeElapsedLabels:

    def test_fails_with_multiple_times(self):
        data = pd.DataFrame({
            "time": pd.to_datetime([
                "2021-01-01T10:00:01Z",
                "2021-01-01T10:00:02Z",
                "2021-01-01T10:00:03Z",
                "2021-01-01T10:00:03.99999Z",
                "2021-01-01T10:00:04.125Z",
            ])
        })
        label_func = utilities.generate_time_elapsed_labels(
            pd.to_datetime("2021-01-01T10:00:01Z"), "time"
        )
        with pytest.raises(ValueError, match="Frame has multiple times"):
            label_func(data)

    def test_works(self):
        data = pd.DataFrame({
            "time": pd.to_datetime([
                "2021-01-01T10:00:04.126Z",
                "2021-01-01T10:00:04.126Z",
                "2021-01-01T10:00:04.126Z",
                "2021-01-01T10:00:04.126Z",
                "2021-01-01T10:00:04.126Z",
            ])
        })
        label_func = utilities.generate_time_elapsed_labels(
            pd.to_datetime("2021-01-01T10:00:01Z"), "time"
        )
        expected = "3.13 s"
        actual = label_func(data)
        assert expected == actual


class TestGenerateLabelsFromColumns:

    @pytest.fixture
    def data(self):
        return pd.DataFrame({
            "int": [1, 2, 3, 4, 5],
            "float": [0.1, 0.2, 0.31313131, 0.45678, 0.5],
            "string": ["one", "two", "three", "four", "five"]
        })

    @pytest.mark.parametrize("column", ["int", "float", "string"])
    def test_works_single_column_no_format(self, data, column):
        label_func = utilities.generate_labels_from_columns([column])
        expected = data[column].astype(str)
        actual = label_func(data)
        pd.testing.assert_series_equal(expected, actual)

    @pytest.mark.parametrize(
        "column,formatter",
        [
            ("int", "{:.2f}"),
            ("int", "{:02d}"),
            ("float", "{:.2f}"),
            ("float", "{:.2%}")
        ]
    )
    def test_works_formatting(self, data, column, formatter):
        label_func = utilities.generate_labels_from_columns([column], column_formatting=[formatter])
        expected = pd.Series(
            [
                formatter.format(value)
                for value in data[column]
            ],  name=column
        )
        actual = label_func(data)
        pd.testing.assert_series_equal(expected, actual)

    def test_works_multiple_columns(self, data):
        label_func = utilities.generate_labels_from_columns(
            ["string", "float"],
            column_formatting=["{:s}:", "{:.2f}"],
            separator=" hey this works "
        )
        expected = pd.Series(
            [
                "{:s}: hey this works {:.2f}".format(string_value, float_value)
                for string_value, float_value in zip(data["string"], data["float"])
            ], name="string"
        )
        actual = label_func(data)
        pd.testing.assert_series_equal(expected, actual)