import os
import pathlib

import pytest

from atomflow.components import *
from atomflow.atom import Atom
from atomflow.iterator import AtomIterator

TEST_FOLDER = pathlib.Path("tests/test_iterator")

@pytest.fixture
def example_atoms() -> list[Atom]:

    atom1 = Atom(IndexComponent(1), ElementComponent("C"), AAResidueComponent("MET"), ChainComponent("A"),
                 ResIndexComponent(1), CoordXComponent(1.0), CoordYComponent(1.0), CoordZComponent(1.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("C"), SectionComponent("ATOM"))

    atom2 = Atom(IndexComponent(2), ElementComponent("N"), AAResidueComponent("GLU"), ChainComponent("B"),
                 ResIndexComponent(2), CoordXComponent(2.0), CoordYComponent(2.0), CoordZComponent(2.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("N"), SectionComponent("ATOM"))

    atom3 = Atom(IndexComponent(3), ElementComponent("O"), AAResidueComponent("HIS"), ChainComponent("B"),
                 ResIndexComponent(3), CoordXComponent(3.0), CoordYComponent(3.0), CoordZComponent(3.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("O"), SectionComponent("ATOM"))

    return [atom1, atom2, atom3]


def test_filter_resname(example_atoms):

    """Atoms can be filtered on residue name with the key 'resname'."""

    (filename,), _ = AtomIterator\
        .from_list(example_atoms) \
        .filter("resname", none_of=["HIS"])\
        .collect()\
        .write(TEST_FOLDER / "test.pdb")

    with open(filename) as file:
        file_text = file.read()
    os.remove(filename)

    true_text = f"ATOM      1  C   MET A   1       1.000   1.000   1.000  1.00  0.00           C  \n"\
                f"ATOM      2  N   GLU B   2       2.000   2.000   2.000  1.00  0.00           N  "

    assert true_text == file_text


def test_filter_chain(example_atoms):

    """Atoms can be filtered on chain with the key 'chain'."""

    (filename,), _ = AtomIterator\
        .from_list(example_atoms) \
        .filter("chain", any_of=["B"])\
        .collect()\
        .write(TEST_FOLDER / "test.pdb")

    with open(filename) as file:
        file_text = file.read()
    os.remove(filename)

    true_text = f"ATOM      2  N   GLU B   2       2.000   2.000   2.000  1.00  0.00           N  \n"\
                f"ATOM      3  O   HIS B   3       3.000   3.000   3.000  1.00  0.00           O  "

    assert true_text == file_text