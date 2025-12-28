import pytest
from typing import Protocol, runtime_checkable

from atomflow.aspects import *
from atomflow.components import *
from tests.test_aspects import test_aspect, second_aspect


@pytest.fixture
def naked_component():

    class NakedComponent(Component):

        """Component without aspects"""

        def __init__(self, value):
            self._value = value

        @property
        def value(self):
            return self._value

    return NakedComponent

@pytest.fixture
def test_component(test_aspect):

    @aspects(test_aspect)
    class TestComponent(Component):

        def __init__(self, value):
            self._value = value

        @property
        def value(self):
            return self._value

    return TestComponent


@pytest.fixture
def second_component(second_aspect):

    @aspects(second_aspect)
    class SecondComponent(Component):

        def __init__(self, item):
            self._item = item

        @property
        def item(self):
            return self._item

    return SecondComponent



def test_aspect_verification(naked_component, test_aspect, second_aspect):

    # Shouldn't raise exception
    aspects(test_aspect)(naked_component)

    # bad_aspect has one property, '_', which NakedComponent doesn't implement
    with pytest.raises(Exception):
        aspects(second_aspect)(naked_component)


def test_prop_name_capture(test_component):

    cmp = test_component("foo")
    assert cmp.get_prop_names() == ["value"]


def test_component_equality(test_component):

    cmp1 = test_component("foo")
    cmp2 = test_component("foo")
    cmp3 = test_component("bar")

    # Components should be defined by their values
    assert cmp1 == cmp2 != cmp3