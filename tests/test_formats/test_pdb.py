import os
import pathlib
import random

import pytest

from atomflow.atom import Atom
from atomflow.components import *
from atomflow.formats import *

TEST_FOLDER = pathlib.Path("tests/test_formats")
PDB_STRUCTURES_FOLDER = pathlib.Path("tests/data/pdb")


@pytest.fixture
def test_atom():

    return Atom(
        PolymerComponent("protein"),
        IndexComponent(1),
        NameComponent("N"),
        AAResidueComponent("MET"),
        ChainComponent("A"),
        ResIndexComponent(1),
        CoordXComponent(1),
        CoordZComponent(1),
        CoordYComponent(1),
        OccupancyComponent(1),
        TemperatureFactorComponent(10),
        ElementComponent("N"),
        )


def test_pdb_line_read(test_atom):

    filename = TEST_FOLDER / "test.pdb"
    simple = "ATOM      1  N   MET A   1       1.000   1.000   1.000  1.00 10.00           N  \n"

    with open(filename, "w") as file:
        file.write(simple)

    file_atom = PDBFormat.read_file(filename)
    os.remove(filename)

    assert file_atom == [test_atom]


def test_pdb_line_write(test_atom):

    filename = TEST_FOLDER / "test.pdb"
    PDBFormat.to_file([test_atom],filename)

    simple = "ATOM      1  N   MET A   1       1.000   1.000   1.000  1.00 10.00           N  \n"

    with open(filename) as file:
        text = file.read()
    os.remove(filename)

    assert text == simple


def test_insufficient_data():

    """If any atoms don't meet the format recipe, the whole write should be rejected."""

    atom = Atom(
        IndexComponent(1),
        AAResidueComponent("MET"),
        ChainComponent("A"),
        ResIndexComponent(1),
        # CoordXComponent(1),  Missing X-coordinate
        CoordZComponent(1),
        CoordYComponent(1),
        ElementComponent("N"),
    )

    with pytest.raises(ValueError):
        PDBFormat.to_file([atom], "")


def test_pdb_read_write(sample_size=10):

    """
    The write method conserves all information gathered by the read method.

    NB: test of all 1000 files takes a while
    """

    test_filename = TEST_FOLDER / "test.pdb"

    pdb_files = [f for f in os.listdir(PDB_STRUCTURES_FOLDER)
                 if os.path.isfile(PDB_STRUCTURES_FOLDER / f)]

    pdb_files = random.sample(pdb_files, sample_size)

    errors = []

    try:
        for filename in pdb_files:
            atoms_original = PDBFormat.read_file(PDB_STRUCTURES_FOLDER / filename)
            PDBFormat.to_file(atoms_original, test_filename)
            atoms_new = PDBFormat.read_file(test_filename)
            assert atoms_original == atoms_new
    except AssertionError as ae:
        raise ae
    except Exception as e:
        errors.append(str(e))
    finally:
        if os.path.exists(test_filename):
            os.remove(test_filename)
        if errors:
            print(f"There were {len(errors)} other errors. First error:")
            print(errors[0])