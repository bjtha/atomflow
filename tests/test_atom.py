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
