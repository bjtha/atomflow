import os
import pathlib
import pytest

from atomflow.formats import *
from atomflow.formats.formats import PDBFormat


def test_pdb_atom_parsing():

    with open("tests/data/atom_sample.txt") as file:
        atom_records = [(line[:80], line[80:90]) for line in file.readlines()]

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
