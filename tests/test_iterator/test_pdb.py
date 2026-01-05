import os
import pathlib

import pytest

from atomflow.components import *
from atomflow.atom import Atom
from atomflow.iterator import AtomIterator, read

TEST_FOLDER = pathlib.Path("tests/test_iterator")

@pytest.fixture
def example_atoms() -> list[Atom]:

    atom1 = Atom(IndexComponent(1), ElementComponent("C"), AAResidueComponent("MET"), ChainComponent("A"),
                 ResIndexComponent(1), CoordXComponent(1.0), CoordYComponent(1.0), CoordZComponent(1.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("C"))

    atom2 = Atom(IndexComponent(2), ElementComponent("N"), AAResidueComponent("GLU"), ChainComponent("B"),
                 ResIndexComponent(2), CoordXComponent(2.0), CoordYComponent(2.0), CoordZComponent(2.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("N"))

    atom3 = Atom(IndexComponent(3), ElementComponent("O"), AAResidueComponent("HIS"), ChainComponent("B"),
                 ResIndexComponent(3), CoordXComponent(3.0), CoordYComponent(3.0), CoordZComponent(3.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("O"))

    return [atom1, atom2, atom3]


def test_single_group(example_atoms):

    """Atoms in the same group are written to the same file."""

    filename = AtomIterator.from_list(example_atoms).collect().write(TEST_FOLDER / "test.pdb")

    with open(filename) as file:
        file_text = file.read()
    os.remove(filename)

    true_text = f"ATOM      1  C   MET A   1       1.000   1.000   1.000  1.00  0.00           C  \n"\
                f"ATOM      2  N   GLU B   2       2.000   2.000   2.000  1.00  0.00           N  \n"\
                f"ATOM      3  O   HIS B   3       3.000   3.000   3.000  1.00  0.00           O  \n"

    assert true_text == file_text


def test_multiple_groups(example_atoms):

    """Atoms in different groups are written to separate files."""

    filenames = AtomIterator\
        .from_list(example_atoms)\
        .group_by("chain")\
        .write(TEST_FOLDER / "test.pdb")

    texts = []

    for filename in filenames:
        with open(filename) as file:
            texts.append(file.read())
        os.remove(filename)

    chain_a, chain_b = texts

    assert chain_a == "ATOM      1  C   MET A   1       1.000   1.000   1.000  1.00  0.00           C  \n"

    assert chain_b == f"ATOM      2  N   GLU B   2       2.000   2.000   2.000  1.00  0.00           N  \n"\
                      f"ATOM      3  O   HIS B   3       3.000   3.000   3.000  1.00  0.00           O  \n"


def test_insufficient_data(example_atoms):

    """If any atoms in a group have insufficient data, the write should fail."""

    # Missing Element
    atom4 = Atom(IndexComponent(4), AAResidueComponent("VAL"), ChainComponent("B"),
                 ResIndexComponent(4), CoordXComponent(4.0), CoordYComponent(4.0), CoordZComponent(4.0))

    bad_atoms = example_atoms + [atom4]

    with pytest.raises(ValueError):
        AtomIterator.from_list(bad_atoms).collect().write("./test.pdb")


def test_filtering(example_atoms):

    """Atoms can be filtered before writing, for example to remove specific residues."""

    water_atom = Atom(IndexComponent(4), ElementComponent("O"), ResidueComponent("HOH"), ChainComponent("B"),
                 ResIndexComponent(4), CoordXComponent(4.0), CoordYComponent(4.0), CoordZComponent(4.0))

    wet_atoms = example_atoms + [water_atom]

    filename = AtomIterator\
        .from_list(wet_atoms) \
        .filter("resname", none_of=["HOH"])\
        .filter("chain", any_of=["B"])\
        .collect()\
        .write(TEST_FOLDER / "test.pdb")

    with open(filename) as file:
        file_text = file.read()
    os.remove(filename)

    true_text = f"ATOM      2  N   GLU B   2       2.000   2.000   2.000  1.00  0.00           N  \n"\
                f"ATOM      3  O   HIS B   3       3.000   3.000   3.000  1.00  0.00           O  \n"

    assert true_text == file_text


def test_read(example_atoms):

    """Read creates an atom iterator from a pdb file."""

    test_filename = TEST_FOLDER / "test.pdb"

    text = f"ATOM      1  C   MET A   1       1.000   1.000   1.000  1.00  0.00           C  \n" \
           f"ATOM      2  N   GLU B   2       2.000   2.000   2.000  1.00  0.00           N  \n" \
           f"ATOM      3  O   HIS B   3       3.000   3.000   3.000  1.00  0.00           O  \n"

    with open(test_filename, "w") as file:
        file.write(text)

    try:
        a_iter = read(test_filename)
    finally:
        os.remove(test_filename)

    atom_a, atom_b, atom_c = example_atoms

    assert list(a_iter) == [(atom_a,), (atom_b,), (atom_c,)]
