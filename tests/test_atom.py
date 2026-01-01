import pytest

from atomflow.atom import *
from tests.test_components import test_component, second_component, test_aspect, second_aspect


def test_add_component(test_aspect, test_component):

    atm = Atom()
    cmp = test_component(value=1)

    # Adding after initialisation
    atm.add(cmp)
    assert atm._by_aspect == {test_aspect: [cmp]}
    assert atm._by_keyword == {"value": [cmp]}

    # Adding during initialisation
    atm = Atom(cmp)
    assert atm._by_aspect == {test_aspect: [cmp]}
    assert atm._by_keyword == {"value": [cmp]}


def test_referencing(test_component):

    cmp = test_component(value=1)
    atm = Atom(cmp)

    # Getting underlying component data through getattr or getitem
    assert atm.value == 1
    assert atm["value"] == 1

    # Raising AttributeError when the data doesn't exist
    with pytest.raises(AttributeError):
        _ = atm.item


def test_aspect_check(test_component, test_aspect, second_aspect):

    cmp = test_component(value=1)
    assert second_aspect not in cmp.aspects  # Not a subclass of second_aspect

    atm = Atom(cmp)

    assert atm.implements(test_aspect)
    assert not atm.implements(second_aspect)


def test_equality(test_component, second_component):

    cmp1 = test_component(value=1)
    cmp2 = second_component(item="A")

    cmp3 = test_component(value=0)

    atom1 = Atom()
    atom1.add(cmp1)
    atom1.add(cmp2)

    atom2 = Atom()
    atom2.add(cmp2)
    atom2.add(cmp1)

    # Atoms with the same components and values should be equal, regardless of the order they were added
    assert atom1 == atom2

    # Atoms with different components or values should not be equal
    atom3 = Atom(cmp1)
    atom4 = Atom(cmp3, cmp2)

    assert atom1 != atom3
    assert atom1 != atom4


def test_representation(test_component):

    atm = Atom(test_component(1))

    short = "Atom(value=1)"
    assert f"{atm:s}" == short

    long = f"Atom(\n"\
    f"\tTestComponent(value=1)\n"\
    f"\t)"
    assert f"{atm:l}" == long

    # Default representation should be short
    assert str(atm) == short
