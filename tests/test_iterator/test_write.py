import os
import pathlib

import pytest

from atomflow.components import *
from atomflow.atom import Atom
from atomflow.iterator import AtomIterator

TEST_FOLDER = pathlib.Path("./tests/test_iterator")


@pytest.fixture
def example_atoms() -> list[Atom]:

    atom1 = Atom(IndexComponent(1), ElementComponent("C"), AAResidueComponent("MET"), ChainComponent("A"),
                 ResIndexComponent(1), CoordXComponent(1.0), CoordYComponent(1.0), CoordZComponent(1.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("C"), EntityComponent("test"))

    atom2 = Atom(IndexComponent(2), ElementComponent("N"), AAResidueComponent("GLU"), ChainComponent("B"),
                 ResIndexComponent(2), CoordXComponent(2.0), CoordYComponent(2.0), CoordZComponent(2.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("N"), EntityComponent("test"))

    atom3 = Atom(IndexComponent(3), ElementComponent("O"), AAResidueComponent("HIS"), ChainComponent("B"),
                 ResIndexComponent(3), CoordXComponent(3.0), CoordYComponent(3.0), CoordZComponent(3.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("O"), EntityComponent("test"))

    return [atom1, atom2, atom3]


def test_write_failure(example_atoms):

    """Write returns a list of all filenames that were written, and all exceptions that occurred."""

    # Missing Element aspect
    atom4 = Atom(IndexComponent(4), AAResidueComponent("VAL"), ChainComponent("B"),
                 ResIndexComponent(4), CoordXComponent(4.0), CoordYComponent(4.0), CoordZComponent(4.0))

    bad_atoms = example_atoms + [atom4]

    filenames, (err,) = AtomIterator.from_list(bad_atoms).collect().write("./test.pdb")

    assert isinstance(err, ValueError)


def test_write_multiple_fasta(example_atoms):

    """Each group of atoms is written to a different fasta file."""

    true_texts = [">test\nM\n", ">test\nE\n", ">test\nH\n"]

    files, errs = AtomIterator.from_list(example_atoms).write(TEST_FOLDER / "test.fasta")

    file_texts = []
    for filename in files:
        with open(filename) as file:
            file_texts.append(file.read())
        os.remove(filename)

    assert true_texts == file_texts


def test_write_single_fasta(example_atoms):

    """Atoms in the same group should be written to one fasta file, ordered by residue index."""

    (filename,), _ = AtomIterator.from_list(example_atoms).collect().write(TEST_FOLDER / "test.fasta")

    with open(filename) as file:
        file_text = file.read()
    os.remove(filename)

    assert ">test\nMEH\n" == file_text


def test_insufficient_fasta_data(example_atoms):

    """The fasta format quietly excludes atoms which don't fit the format recipe."""

    # Lacks index
    atom_d = Atom(AAResidueComponent("GLY"), EntityComponent("test"))

    bad_atoms = example_atoms + [atom_d]
    (filename,), _ = AtomIterator.from_list(bad_atoms).collect().write(TEST_FOLDER / "test.fasta")

    with open(filename) as file:
        file_text = file.read()
    os.remove(filename)

    assert ">test\nMEH\n" == file_text


def test_write_single_pdb(example_atoms):

    """Atoms in the same group are written to the same .pdb file."""

    (filename,), _ = AtomIterator.from_list(example_atoms).collect().write(TEST_FOLDER / "test.pdb")

    with open(filename) as file:
        file_text = file.read()
    os.remove(filename)

    true_text = f"ATOM      1  C   MET A   1       1.000   1.000   1.000  1.00  0.00           C  \n"\
                f"ATOM      2  N   GLU B   2       2.000   2.000   2.000  1.00  0.00           N  \n"\
                f"ATOM      3  O   HIS B   3       3.000   3.000   3.000  1.00  0.00           O  \n"

    assert true_text == file_text


def test_write_multiple_pdb(example_atoms):

    """Atoms in different groups are written to separate .pdb files."""

    filenames, _ = AtomIterator\
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


def test_outpath_formating(example_atoms):

    """Output file names can be defined dynamically, replacing named aspect tokens with the values
    from the first atom of the group being written."""

    filenames, _ = AtomIterator \
        .from_list(example_atoms) \
        .group_by("chain") \
        .write(TEST_FOLDER / "test_chain{}_res{}.pdb", path_fmt=("chain", "resindex"))

    for filename in filenames:
        os.remove(filename)

    assert filenames == [str(TEST_FOLDER / "test_chainA_res1.pdb"), str(TEST_FOLDER / "test_chainB_res2.pdb")]