import pandas as pd
import pytest

import ptplot.ptplot as pt
from ptplot.animation import Animation
from ptplot.core import Layer


class TestInternalGetClassInstanceFromLayers:
    @pytest.fixture(scope="function")
    def layer(self):
        class TestLayer(Layer):
            pass

        return TestLayer

    def test_returns_none_if_no_layer(self, layer):
        class OtherLayer(Layer):
            pass
        plot = pt.PTPlot(pd.DataFrame()) + layer()
        assert plot._get_class_instance_from_layers(OtherLayer) is None

    def test_returns_layer_if_exists(self, layer):
        test_layer = layer()
        plot = pt.PTPlot(pd.DataFrame()) + test_layer
        assert plot._get_class_instance_from_layers(layer) == test_layer

    def test_returns_layer_if_subclass(self, layer):
        class TestSubclass(layer):
            def extra_method(self):
                return "extra method"
        plot = pt.PTPlot(pd.DataFrame()) + TestSubclass()
        assert plot._get_class_instance_from_layers(layer).extra_method() == "extra method"

    def test_errors_with_multiple_layers(self, layer):
        plot = pt.PTPlot(pd.DataFrame()) + layer() + layer()
        with pytest.raises(ValueError):
            plot._get_class_instance_from_layers(layer)


class TestInternalApplyMapping:
    @pytest.fixture(scope="function")
    def input_data(self):
        df = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [6, 7, 8, 9, 10]
        })
        return df

    def test_passes_column_name(self, input_data):
        expected = pd.Series([1, 2, 3, 4, 5], name="a")
        actual = pt._apply_mapping(input_data, "a")
        pd.testing.assert_series_equal(expected, actual)

    def test_copies_when_passed_column_name(self, input_data):
        mapped_data = pt._apply_mapping(input_data, "b")
        input_data.loc[input_data["a"] > 2, "b"] = 999
        expected_mapped_data = pd.Series([6, 7, 8, 9, 10], name="b")
        expected_input_data = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [6, 7, 999, 999, 999]
        })
        pd.testing.assert_series_equal(mapped_data, expected_mapped_data)
        pd.testing.assert_frame_equal(input_data, expected_input_data)

    def test_preserves_index(self, input_data):
        input_data.index = [2, 4, 8, 16, 32]
        expected = pd.Series([1, 2, 3, 4, 5], name="a", index=[2, 4, 8, 16, 32])
        actual = pt._apply_mapping(input_data, "a")
        pd.testing.assert_series_equal(expected, actual)

    def test_works_with_arithmetic(self, input_data):
        arithmetic = "a *b"
        expected = pd.Series([6., 14., 24., 36., 50.], name=arithmetic)
        actual = pt._apply_mapping(input_data, arithmetic)
        pd.testing.assert_series_equal(expected, actual)

    def test_works_with_conditional(self, input_data):
        conditional = "3*a > b"
        expected = pd.Series([False, False, True, True, True], name=conditional)
        actual = pt._apply_mapping(input_data, conditional)
        pd.testing.assert_series_equal(expected, actual)