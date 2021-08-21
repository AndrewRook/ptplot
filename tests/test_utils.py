import pytest

from ptplot import utils


class TestInternalUnionKwargs:
    def test_works_with_no_protected_kwargs(self):
        pass

    def test_errors_when_overriding_protected_kwargs(self):
        pass

    def test_non_protected_overrides_work(self):
        pass

    def test_rightmost_dictionary_takes_precedence(self):
        pass