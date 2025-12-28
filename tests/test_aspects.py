from typing import Protocol, runtime_checkable

import pytest

from atomflow.aspects import *

@pytest.fixture
def test_aspect():

    @runtime_checkable
    class TestAspect(Aspect, Protocol):

        @property
        def value(self) -> str: pass

    return TestAspect


@pytest.fixture
def second_aspect():

    @runtime_checkable
    class SecondAspect(Aspect, Protocol):

        @property
        def item(self) -> str: pass

    return SecondAspect


def test_protocol_adoption(test_aspect):

    class Adoptee:

        @property
        def value(self) -> str:
            return "hello"

    assert isinstance(Adoptee, test_aspect)