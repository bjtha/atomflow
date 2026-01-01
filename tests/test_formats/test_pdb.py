import os
import pathlib

import pytest

from atomflow.atom import Atom
from atomflow.components import *
from atomflow.formats import *

PDB_STRUCTURES_FOLDER = pathlib.Path("tests/data/pdb")
PDB_ATOM_SAMPLE = pathlib.Path("tests/data/pdb_atom_sample.txt")


@pytest.fixture
def example_pdb_atom_records() -> list[tuple]:

    """Provides records from PDB atom sample file, as a list of (record, source_file)"""

    if os.path.exists(PDB_ATOM_SAMPLE):
        with open(PDB_ATOM_SAMPLE) as file:
            return [(line[:80], line[80:90]) for line in file.readlines()]
    else:
        msg = f"PDB atom sample file not found at '{PDB_ATOM_SAMPLE}'. See tests.utils for functions to build one."
        raise FileNotFoundError(msg)

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

def test_pdb_atom_parsing(example_pdb_atom_records):

    """PDB ATOM and HETATM records should convert into Atom objects and back again without loss."""

    source, record, line_w, atom = (None,)*4

    try:
        for record, source in example_pdb_atom_records:
            atom = PDBFormat.atom_from_line(record)
            line_w = PDBFormat.line_from_atom(atom)

            assert line_w == record

    except AssertionError as e:

        # Print vertically aligned to make differences clearer
        print(f"{source: <12}{record}")
        print(f"{"recon": <12}{line_w}")
        print(f"Atom representation: {atom}")

        raise e

    except Exception as e:
        raise e


def test_pdb_file_read(test_atom):

    filename = "test.pdb"
    simple = "ATOM      1  N   MET A   1       1.000   1.000   1.000  1.00 10.00           N  \n"

    with open(filename, "w") as file:
        file.write(simple)

    file_atom = PDBFormat.read_file(filename)
    os.remove(filename)

    assert file_atom == [test_atom]


def test_pdb_file_write(test_atom):

    filename = "./test.pdb"
    PDBFormat.to_file([test_atom],filename)

    simple = "ATOM      1  N   MET A   1       1.000   1.000   1.000  1.00 10.00           N  \n"

    with open(filename) as file:
        text = file.read()
    os.remove(filename)

    assert text == simple


def test_full_pdb_read_write():

    """
    The write method should conserve all information gathered by the read method.

    NB: takes a while
    """

    pdb_files = [f for f in os.listdir(PDB_STRUCTURES_FOLDER)
                 if os.path.isfile(PDB_STRUCTURES_FOLDER / f)]

    try:
        for filename in pdb_files:
            atoms_original = PDBFormat.read_file(PDB_STRUCTURES_FOLDER / filename)
            PDBFormat.to_file(atoms_original, "./temp.pdb")
            atoms_new = PDBFormat.read_file("./temp.pdb")

            assert atoms_original == atoms_new

    except AssertionError as e:
        raise e

    except Exception as e:
        print(str(e))

    finally:
        os.remove("./temp.pdb")