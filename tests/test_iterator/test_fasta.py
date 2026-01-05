import os
import pathlib

import pytest

from atomflow.components import *
from atomflow.atom import Atom
from atomflow.iterator import AtomIterator, read

TEST_FOLDER = pathlib.Path("./tests/test_iterator")

@pytest.fixture
def example_atoms() -> list[Atom]:
    atom_a = Atom(AAResidueComponent("VAL"), ResIndexComponent(2), EntityComponent("test"))
    atom_b = Atom(AAResidueComponent("MET"), ResIndexComponent(1), EntityComponent("test"))
    atom_c = Atom(AAResidueComponent("ASP"), ResIndexComponent(3), EntityComponent("test"))

    return [atom_a, atom_b, atom_c]


def test_write_multiple(example_atoms):

    """Each group of atoms is written to a different file."""

    true_texts = [">test\nV\n", ">test\nM\n", ">test\nD\n"]

    files = AtomIterator.from_list(example_atoms).write(TEST_FOLDER / "test.fasta")

    file_texts = []
    for filename in files:
        with open(filename) as file:
            file_texts.append(file.read())
        os.remove(filename)

    assert true_texts == file_texts


def test_write_single(example_atoms):

    """Atoms in the same group should be written to one file, ordered by residue index."""

    filename = AtomIterator.from_list(example_atoms).collect().write(TEST_FOLDER / "test.fasta")

    with open(filename) as file:
        file_text = file.read()
    os.remove(filename)

    assert ">test\nMVD\n" == file_text


def test_insufficient_data(example_atoms):

    """The write quietly excludes atoms which don't fit the format recipe."""

    # Lacks index
    atom_d = Atom(AAResidueComponent("HIS"), EntityComponent("test"))

    bad_atoms = example_atoms + [atom_d]
    filename = AtomIterator.from_list(bad_atoms).collect().write(TEST_FOLDER / "test.fasta")

    with open(filename) as file:
        file_text = file.read()
    os.remove(filename)

    assert ">test\nMVD\n" == file_text


def test_read(example_atoms):

    """Read creates an atom iterator from any valid file with a fasta extension."""

    test_text = ">test\nMVD\n"
    test_filename = TEST_FOLDER / "test.fasta"

    with open(test_filename, "w") as file:
        file.write(test_text)

    try:
        a_iter = read(test_filename)
    finally:
        os.remove(test_filename)

    atom_v, atom_m, atom_d = example_atoms

    assert list(a_iter) == [(atom_m,), (atom_v,), (atom_d,)]
