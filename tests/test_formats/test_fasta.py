import os

from atomflow.atom import Atom
from atomflow.components import *
from atomflow.formats import FastaFormat


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


def test_empty_file():

    """Files with empty sequences should return no atoms for those sequences, failing quietly."""

    simple_fasta = ">empty"
    filename = "test.fasta"

    with open(filename, "w") as file:
        file.write(simple_fasta)

    atoms = FastaFormat.read_file(filename)

    os.remove(filename)

    assert atoms == []

def test_write_single_chain():

    """Single chains should be written as single sequences"""

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
    raise NotImplementedError


def test_write_identical_chains():
    raise NotImplementedError


def test_reject_unparseable_sequence():
    raise NotImplementedError


def test_full_read_write_proteins():
    raise  NotImplementedError

# Format expectations:
# * Empty fasta files return an empty list
# * Sequences represented by multiple identical chains are only written out once
# * Sequences with residue codes that don't fit into any one format (e.g. MU...) raise an error
# * Write method should conserve all information gathered by the read method
# * Non-polymer residues shouldn't be written out
# * Residues from different polymers should write to different files
# * Residues from different chains, but the same polymer type, should write to one file