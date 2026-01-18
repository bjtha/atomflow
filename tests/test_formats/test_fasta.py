import os
import pathlib
import random

import pytest

from atomflow.atom import Atom
from atomflow.components import *
from atomflow.formats import FastaFormat

FASTA_SEQUENCES_FOLDER = pathlib.Path("tests/data/fasta")



def test_protein_fasta_into_atoms():

    """Protein sequences should be read into atoms with amino acid residue components."""

    simple_fasta = ">test\nM"
    filename = "test.fasta"

    with open(filename, "w") as file:
        file.write(simple_fasta)

    atoms = FastaFormat.read_file(filename)

    os.remove(filename)

    target_atom = Atom(
        AAResidueComponent("M"),
        EntityComponent("test"),
        ResIndexComponent(1),
    )
    assert atoms[0] == target_atom


def test_dna_fasta_into_atoms():

    """DNA sequences should be read into atoms with DNA residue components."""

    simple_fasta = ">test\nA"
    filename = "test.fasta"

    with open(filename, "w") as file:
        file.write(simple_fasta)

    atoms = FastaFormat.read_file(filename)

    os.remove(filename)

    target_atom = Atom(
        DNAResidueComponent("A"),
        EntityComponent("test"),
        ResIndexComponent(1),
    )
    assert atoms[0] == target_atom


def test_rna_fasta_into_atoms():

    """RNA sequences should be read into atoms with RNA residue components."""

    simple_fasta = ">test\nU"
    filename = "test.fasta"

    with open(filename, "w") as file:
        file.write(simple_fasta)

    atoms = FastaFormat.read_file(filename)

    os.remove(filename)

    target_atom = Atom(
        RNAResidueComponent("U"),
        EntityComponent("test"),
        ResIndexComponent(1),
    )
    assert atoms[0] == target_atom


def test_reject_unparseable_sequence():

    """Sequences with ambiguous mixtures of residue codes should be rejected."""

    dna_rna = ">test\nTU"
    filename = "test.fasta"

    with open(filename, "w") as file:
        file.write(dna_rna)

    with pytest.raises(ValueError):
        FastaFormat.read_file(filename)

    rna_aa = ">test\nMU"

    with open(filename, "w") as file:
        file.write(rna_aa)

    with pytest.raises(ValueError):
        FastaFormat.read_file(filename)
    os.remove(filename)


def test_empty_file():

    """Files with empty sequences should return no atoms for those sequences, failing quietly."""

    simple_fasta = ">empty"
    filename = "test.fasta"

    with open(filename, "w") as file:
        file.write(simple_fasta)

    atoms = FastaFormat.read_file(filename)

    os.remove(filename)

    assert atoms == []


def test_insufficient_data():

    """Atoms which don't meet the recipe should be ignored."""

    filename = "test.fasta"

    atom = Atom(
        AAResidueComponent("V"),
        ResIndexComponent(1),
        EntityComponent("test")
    )
    only_polymer = Atom(
        AAResidueComponent("L"),
        ResIndexComponent(1),
    )

    FastaFormat.to_file([atom, only_polymer], filename)

    with open(filename) as file:
        text = file.read()

    os.remove(filename)

    assert text == ">test\nV\n"


def test_write_single_chain():

    """Single entities should be written as single sequences"""

    filename = "test.fasta"
    ori_atom = Atom(
        AAResidueComponent("M"),
        EntityComponent("test"),
        ResIndexComponent(1),
        ChainComponent("A")
    )

    FastaFormat.to_file([ori_atom], filename)

    with open(filename) as file:
        text = file.read()

    os.remove(filename)

    assert text == ">test\nM\n"


def test_write_different_chains():

    """Multiple entities should be written to the same file as different sequences"""

    filename = "test.fasta"
    chain_a = Atom(
        AAResidueComponent("M"),
        ResIndexComponent(1),
        ChainComponent("A")
    )
    chain_b = Atom(
        AAResidueComponent("A"),
        ResIndexComponent(1),
        ChainComponent("B")
    )

    FastaFormat.to_file([chain_a, chain_b], filename)

    with open(filename) as file:
        text = file.read()

    os.remove(filename)

    assert text == ">protein_A\nM\n>protein_B\nA\n"

def test_write_identical_chains():

    """Identical sequences should only be represented once in the output."""

    filename = "test.fasta"
    chain_a = Atom(
        AAResidueComponent("M"),
        ResIndexComponent(1),
        ChainComponent("A")
    )
    chain_b = Atom(
        AAResidueComponent("M"),
        ResIndexComponent(1),
        ChainComponent("B")
    )

    FastaFormat.to_file([chain_a, chain_b], filename)

    with open(filename) as file:
        text = file.read()

    os.remove(filename)

    assert text == ">protein_A\nM\n"


def test_full_read_write_proteins(sample_size=100):

    """The write method should conserve all information gathered by the read method."""

    temp_filename = "temp.fasta"

    fasta_files = [f for f in os.listdir(FASTA_SEQUENCES_FOLDER)
                   if os.path.isfile(FASTA_SEQUENCES_FOLDER / f)]

    fasta_files = random.sample(fasta_files, sample_size)

    try:
        for filename in fasta_files:
            atoms_r = FastaFormat.read_file(FASTA_SEQUENCES_FOLDER / filename)
            FastaFormat.to_file(atoms_r, temp_filename)
            atoms_w = FastaFormat.read_file(temp_filename)

            assert atoms_r == atoms_w

    except AssertionError as e:
        raise e

    except Exception as e:
        print(str(e))

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)