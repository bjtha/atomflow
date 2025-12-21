import pytest

from atomflow.components import *
from tests.test_aspects import example_aspect, bad_aspect

@pytest.fixture
def naked_component() -> type[Component]:

    class NakedComponent(Component):

        def __init__(self, value):
            self._value = value

        @property
        def value(self) -> str:
            return self._value

    return NakedComponent


@pytest.fixture
def example_component(naked_component, example_aspect) -> type[Component]:

    @aspects(example_aspect)
    class TestComponent(Component):

        def __init__(self, value):
            self._value = value

        @property
        def value(self) -> str:
            return self._value

    return TestComponent

def test_aspect_verification(example_aspect, bad_aspect, naked_component):

    # Shouldn't raise exception
    aspects(example_aspect)(naked_component)

    # bad_aspect has one property, '_', which TestComponent doesn't implement
    with pytest.raises(Exception):
        aspects(bad_aspect)(naked_component)


def test_prop_name_capture(example_component):

    comp = example_component("foo")
    assert comp.get_prop_names() == ["value"]
