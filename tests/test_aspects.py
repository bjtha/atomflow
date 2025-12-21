import pytest

from atomflow.aspects import *

@pytest.fixture
def example_aspect():

    @runtime_checkable
    class TestAspect(Aspect, Protocol):

        @property
        def value(self) -> str: pass

    return TestAspect

@pytest.fixture
def bad_aspect():

    @runtime_checkable
    class BadAspect(Aspect, Protocol):

        @property
        def _(self) -> str: pass

    return BadAspect


def test_protocol_adoption(example_aspect):

    class Adoptee:

        @property
        def value(self) -> str:
            return "hello"

    assert isinstance(Adoptee, example_aspect)