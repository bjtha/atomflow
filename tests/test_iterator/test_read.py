import os
import pathlib

from atomflow.components import *
from atomflow.atom import Atom
from atomflow.iterator import read

TEST_FOLDER = pathlib.Path("./tests/test_iterator")


def test_read_fasta():
    """Read creates an atom iterator from any valid file with a fasta extension."""

    test_text = ">test\nMVD\n"
    test_filename = TEST_FOLDER / "test.fasta"

    with open(test_filename, "w") as file:
        file.write(test_text)

    try:
        a_iter = read(test_filename)
    finally:
        os.remove(test_filename)

    atom_m = Atom(ResidueComponent("MET"), ResIndexComponent(1), ChainComponent("A"))
    atom_v = Atom(ResidueComponent("VAL"), ResIndexComponent(2), ChainComponent("A"))
    atom_d = Atom(ResidueComponent("ASP"), ResIndexComponent(3), ChainComponent("A"))

    assert list(a_iter) == [(atom_m,), (atom_v,), (atom_d,)]


def test_read_pdb():

    """Read creates an atom iterator from a pdb file."""

    test_filename = TEST_FOLDER / "test.pdb"

    text = f"ATOM      1  C   MET A   1       1.000   1.000   1.000  1.00  0.00           C  \n" \
           f"ATOM      2  N   GLU B   2       2.000   2.000   2.000  1.00  0.00           N  \n" \
           f"ATOM      3  O   HIS B   3       3.000   3.000   3.000  1.00  0.00           O  "

    with open(test_filename, "w") as file:
        file.write(text)

    try:
        a_iter = read(test_filename)
    finally:
        os.remove(test_filename)

    atom_m = Atom(IndexComponent(1), ElementComponent("C"), ResidueComponent("MET"), ChainComponent("A"),
                 ResIndexComponent(1), CoordXComponent(1.0), CoordYComponent(1.0), CoordZComponent(1.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("C"), SectionComponent("ATOM"))

    atom_e = Atom(IndexComponent(2), ElementComponent("N"), ResidueComponent("GLU"), ChainComponent("B"),
                 ResIndexComponent(2), CoordXComponent(2.0), CoordYComponent(2.0), CoordZComponent(2.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("N"), SectionComponent("ATOM"))

    atom_h = Atom(IndexComponent(3), ElementComponent("O"), ResidueComponent("HIS"), ChainComponent("B"),
                 ResIndexComponent(3), CoordXComponent(3.0), CoordYComponent(3.0), CoordZComponent(3.0),
                 OccupancyComponent(1), TemperatureFactorComponent(0), NameComponent("O"), SectionComponent("ATOM"))

    assert list(a_iter) == [(atom_m,), (atom_e,), (atom_h,)]