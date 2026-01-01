import pytest

from atomflow.components import *

@pytest.fixture
def test_aspect():
    return Aspect("value")

@pytest.fixture
def second_aspect():
    return Aspect("item")


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

    # Naked component doesn't implement 'item' from SecondAspect
    with pytest.raises(Exception):
        aspects(second_aspect)(naked_component)


def test_prop_name_capture(test_component):

    cmp = test_component("foo")
    assert cmp.get_property_names() == ["value"]


def test_component_equality(test_component):

    cmp1 = test_component("foo")
    cmp2 = test_component("foo")
    cmp3 = test_component("bar")

    # Components with the same value should be equal
    assert cmp1 == cmp2 != cmp3


def test_instance_caching(test_component):

    cmp1 = test_component("foo")
    cmp2 = test_component("foo")

    assert cmp1 is not cmp2

    cached_component = cache_instances(test_component)

    # When caching is applied, instances with the same value should be the same object
    c_cmp1 = cached_component("foo")
    c_cmp2 = cached_component("foo")

    assert c_cmp1 is c_cmp2