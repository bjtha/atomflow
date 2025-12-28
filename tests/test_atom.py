import pytest

from atomflow.atom import *
from tests.test_aspects import test_aspect, second_aspect
from tests.test_components import test_component, second_component


def test_add_component(test_aspect, test_component):

    atom = Atom()
    cmp = test_component(value=1)

    # Adding after initialisation
    atom.add(cmp)
    assert atom._by_aspect == {test_aspect: [cmp]}
    assert atom._by_keyword == {"value": [cmp]}

    # Adding during initialisation
    atom = Atom(cmp)
    assert atom._by_aspect == {test_aspect: [cmp]}
    assert atom._by_keyword == {"value": [cmp]}


def test_referencing(test_component):

    cmp = test_component(value=1)
    atom = Atom(cmp)

    # Getting underlying component data through getattr or getitem
    assert atom.value == 1
    assert atom["value"] == 1

    # Raising AttributeError when the data doesn't exist
    with pytest.raises(AttributeError):
        _ = atom.item


def test_aspect_check(test_component, test_aspect, second_aspect):

    cmp = test_component(value=1)
    assert second_aspect not in cmp.aspects  # Not a subclass of second_aspect

    atom = Atom(cmp)

    assert atom.implements(test_aspect)
    assert not atom.implements(second_aspect)


def test_component_check(test_component, second_component):

    atom = Atom(test_component(value=1))

    assert atom.has(test_component)
    assert not atom.has(second_component)


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

    atom = Atom(test_component(1))

    short = "Atom(value=1)"
    assert f"{atom:s}" == short

    long = f"Atom(\n"\
    f"\tTestComponent(value=1)\n"\
    f"\t)"
    assert f"{atom:l}" == long

    # Default representation should be short
    assert str(atom) == short
