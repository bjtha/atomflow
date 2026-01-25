import os
import pathlib
import random

import pytest

from atomflow.atom import Atom
from atomflow.components import *
from atomflow.formats import FastaFormat

DATA_FOLDER = pathlib.Path("tests/data/fasta")


def test_protein_fasta_into_atoms():

    """Protein sequences should be read into atoms with amino acid residue components."""

    simple_fasta = ">test\nM"
    filename = "test.fasta"

    with open(filename, "w") as file:
        file.write(simple_fasta)

    atoms = FastaFormat.read_file(filename)

    os.remove(filename)

    target_atom = Atom(
        ResidueComponent("MET"),
        ResIndexComponent(1),
        ChainComponent("A")
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
        ResidueComponent("DA"),
        ResIndexComponent(1),
        ChainComponent("A")
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
        ResidueComponent("U"),
        ResIndexComponent(1),
        ChainComponent("A")
    )
    assert atoms[0] == target_atom


def test_reject_unparseable_sequence():

    """Sequences with ambiguous mixtures of residue codes should be rejected."""

    dna_rna = ">test\nTUJ"
    filename = "test.fasta"

    with open(filename, "w") as file:
        file.write(dna_rna)

    with pytest.raises(ValueError):
        FastaFormat.read_file(filename)


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
        ResidueComponent("VAL"),
        ResIndexComponent(1),
    )
    only_polymer = Atom(
        ResidueComponent("HOH"),
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
        ResidueComponent("MET"),
        ResIndexComponent(1),
        ChainComponent("A")
    )

    FastaFormat.to_file([ori_atom], filename)

    with open(filename) as file:
        text = file.read()

    os.remove(filename)

    assert text == ">test_A\nM\n"


def test_write_different_chains():

    """Multiple entities should be written to the same file as different sequences"""

    filename = "test.fasta"
    chain_a = Atom(
        ResidueComponent("MET"),
        ResIndexComponent(1),
        ChainComponent("A")
    )
    chain_b = Atom(
        ResidueComponent("ALA"),
        ResIndexComponent(1),
        ChainComponent("B")
    )

    FastaFormat.to_file([chain_a, chain_b], filename)

    with open(filename) as file:
        text = file.read()

    os.remove(filename)

    assert text == ">test_A\nM\n>test_B\nA\n"

def test_write_identical_chains():

    """Identical sequences should only be represented once in the output."""

    filename = "test.fasta"
    chain_a = Atom(
        ResidueComponent("MET"),
        ResIndexComponent(1),
        ChainComponent("A")
    )
    chain_b = Atom(
        ResidueComponent("MET"),
        ResIndexComponent(1),
        ChainComponent("B")
    )

    FastaFormat.to_file([chain_a, chain_b], filename)

    with open(filename) as file:
        text = file.read()

    os.remove(filename)

    assert text == ">test_A\nM\n"


def test_full_read_write_proteins(sample_size=100):

    """The write method should conserve all information gathered by the read method."""

    test_filename = "temp.fasta"

    fasta_files = [f for f in os.listdir(DATA_FOLDER)
                   if os.path.isfile(DATA_FOLDER / f)]

    fasta_files = random.sample(fasta_files, sample_size)

    mismatches = []
    other_errors = []
    pass_count = 0

    for filename in fasta_files:
        try:
            original = FastaFormat.read_file(DATA_FOLDER / filename)
            FastaFormat.to_file(original, test_filename)
            new = FastaFormat.read_file(test_filename)
            assert original == new
            pass_count += 1
        except AssertionError as ae:
            mismatches.append((filename, ae))
        except Exception as e:
            other_errors.append((filename, e))

    if os.path.exists(test_filename):
        os.remove(test_filename)

    print(f"{pass_count = }")

    if mismatches:
        filename, error = mismatches.pop()
        print(f"There were {len(mismatches)+1} mismatches. First ({filename}):")
        raise error

    if other_errors:
        filename, error = other_errors.pop()
        print(f"There were {len(other_errors)+1} other errors. First ({filename}):")
        raise error
