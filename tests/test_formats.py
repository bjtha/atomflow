import os
import pathlib

import pytest

from atomflow.atom import Atom
from atomflow.components import *
from atomflow.formats import *

PDB_STRUCTURES_FOLDER = pathlib.Path("tests/data/structures/pdb")
PDB_ATOM_SAMPLE = pathlib.Path("tests/data/pdb_atom_sample.txt")


@pytest.fixture
def example_pdb_atoms() -> list[tuple]:

    """Provides records from PDB atom sample file, as a list of (record, source_file)"""

    if os.path.exists(PDB_ATOM_SAMPLE):
        with open(PDB_ATOM_SAMPLE) as file:
            return [(line[:80], line[80:90]) for line in file.readlines()]
    else:
        msg = f"PDB atom sample file not found at '{PDB_ATOM_SAMPLE}'. See tests.utils for functions to build one."
        raise FileNotFoundError(msg)


def test_pdb_atom_parsing(example_pdb_atoms):

    """
    Tests that PDB atom/hetatm records can be converted into Atom objects and back again without loss.

    :param example_pdb_atoms:
    :return:
    """

    atom_records = example_pdb_atoms

    mismatches = []

    for record, source in atom_records:
        atom = PDBFormat.atom_from_line(record)
        reconstituted = PDBFormat.line_from_atom(atom)

        if reconstituted != record:
            mismatches.append((source, record, atom, reconstituted))

    if len(mismatches) > 0:
        mm = mismatches[0]
        source, original, atom, recon = mm
        print(f"{source: <12}{original}")
        print(f"{"recon": <12}{recon}")
        print(f"Atom representation: {atom}")

        raise Exception(f"{len(mismatches)} mismatches:")


def test_pdb_file_read():

    file_atom = PDBFormat.read_file(PDB_STRUCTURES_FOLDER / "simple.pdb")

    test_atom = [
        Atom(
            PolymerComponent("protein"),
            IndexComponent(1),
            NameComponent("N"),
            ResNameComponent("MET"),
            ChainComponent("A"),
            ResIndexComponent(1),
            CoordinatesComponent(1, 1, 1),
            OccupancyComponent(1),
            TemperatureFactorComponent(10),
            ElementComponent("N"),
        )
    ]

    assert file_atom == test_atom