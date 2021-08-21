import pytest

from ptplot import utils


class TestInternalUnionKwargs:
    def test_works_with_no_protected_kwargs(self):
        expected = {"a": 1, "b": 2, "c": 3}
        actual = utils._union_kwargs({}, expected)
        assert actual == expected

    def test_errors_when_overriding_protected_kwargs(self):
        with pytest.raises(KeyError, match="The following keywords are protected and cannot be overridden: {\'protected\'}"):
            utils._union_kwargs({"protected": 1}, {"protected": 2, "unprotected": 3})

    def test_non_protected_overrides_work(self):
        expected = {"a": 1, "b": 3, "c": 9}
        actual = utils._union_kwargs(
            {"a": 1},
            {"b": 1, "c": 4},
            {"c": 9},
            {"b": 3}
        )
        assert actual == expected

    def test_doesnt_modify_dictionaries(self):
        protected_kwargs = {"a": 1, "b": 2}
        unprotected_one = {"c": 3, "d": 4}
        unprotected_two = {"c": 7, "e": 9}
        _ = utils._union_kwargs(
            protected_kwargs.copy(),
            unprotected_one.copy(),
            unprotected_two.copy()
        )
        assert protected_kwargs == {"a": 1, "b": 2}
        assert unprotected_one == {"c": 3, "d": 4}
        assert unprotected_two == {"c": 7, "e": 9}
