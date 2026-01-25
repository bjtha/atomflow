import os
import pathlib
import random

import pytest

from atomflow.atom import Atom
from atomflow.components import *
from atomflow.formats import CIFFormat

TEST_FOLDER = pathlib.Path("tests/test_formats")
DATA_FOLDER = pathlib.Path("tests/data/cif")

@pytest.fixture
def example_atom() -> Atom:

    return Atom(
        SectionComponent("ATOM"),
        IndexComponent(1),
        ElementComponent("C"),
        NameComponent("CA"),
        ResidueComponent("MET"),
        ChainComponent("A"),
        ResIndexComponent(1),
        CoordXComponent(1),
        CoordYComponent(2),
        CoordZComponent(3),
        OccupancyComponent(1),
        TemperatureFactorComponent(10),
    )

def test_extract_data_items():

    """Single data items and text blocks are extracted and compiled into a dict."""

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        'data_',
        "#",
        "_info.item      1",
        "_info.name      A",
        "_info.text",
        ";The quick brown",
        " fox jumped over",
        " the lazy dog.",
        ";",
        "_info.cost     10",
        "_info.title",
        ";",
        "Pride and Prejudice",
        ";",
        "_info.lyric",
        ";I love you like a rose loves rainwater",
        ";",
        "#",
    ])

    with open(file_name, "w") as file:
        file.write(text)

    try:
        data = CIFFormat._extract_data(file_name)
    finally:
        os.remove(file_name)

    assert data == {"data_":
                        {"_info":
                             {"item": "1",
                              "name": "A",
                              "text": "The quick brown fox jumped over the lazy dog.",
                              "cost": "10",
                              "title": "Pride and Prejudice",
                              "lyric": "I love you like a rose loves rainwater"}}}

def test_extract_data_item_failures():

    # Read fails if text block is interrupted.

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "data_",
        "#",
        "_info.text",
        "; A lady sat upon a bridge,",
        "#",  # Block ended without a ';'
    ])

    with open(file_name, "w") as file:
        file.write(text)

    with pytest.raises(ValueError) as exc:
        CIFFormat._extract_data(file_name)
    os.remove(file_name)
    assert "Unexpected end of text block on line" in str(exc.value)

    # It also fails if a data item has more than one value.

    text = "\n".join([
        "data_",
        "#",
        "_info.list   1   2",
        "#"
    ])

    with open(file_name, "w") as file:
        file.write(text)

    with pytest.raises(ValueError) as exc:
        CIFFormat._extract_data(file_name)
    os.remove(file_name)
    assert "Too many data items on line" in str(exc.value)

def test_extract_data_tables():

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "data_",
        "#",
        "loop_",
        "_info.name",
        "_info.count",
        "_info.description",
        "A 3 'red and bouncy'",
        "B 2 'soft and sticky'",
        "#"
    ])

    with open(file_name, "w") as file:
        file.write(text)

    try:
        data = CIFFormat._extract_data(file_name)
    finally:
        os.remove(file_name)

    assert data == {"data_":
                        {"_info":
                             {"name": ["A", "B"],
                              "count": ["3", "2"],
                              "description": ["red and bouncy", "soft and sticky"]}}}


def test_extract_data_selection():

    """If provided, only named data categories are extracted."""

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "data_",
        "#",
        "_info.item      1",
        "_info.text",
        ";The quick brown",
        " fox jumped over",
        " the lazy dog.",
        ";",
        "#",
        "_type.name      A",
        "#"
    ])

    with open(file_name, "w") as file:
        file.write(text)

    try:
        data = CIFFormat._extract_data(file_name, categories=("_type",))
    finally:
        os.remove(file_name)

    assert data == {"data_": {"_type": {"name": "A"}}}


def test_extract_data_table_failures():

    # Read fails if there's a mismatch between the number of declared fields and the number of data items

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "data_",
        "#",
        "loop_",
        "_info.name",
        "_info.count", # Two fields
        "A 3 'red and bouncy'",
        "B 2 'soft and sticky'", # Three values
        "#"
    ])

    with open(file_name, "w") as file:
        file.write(text)

    with pytest.raises(ValueError) as exc:
        CIFFormat._extract_data(file_name)
    os.remove(file_name)
    assert "zip() argument 2" in str(exc.value)


def test_write_data_items():

    file_name = TEST_FOLDER / "test.cif"

    data = {"data_":
                {"_info":
                     {"item": "1",
                      "name": "A"}}}

    true_text = "\n".join([
        "data_",
        "#",
        "_info.item 1",
        "_info.name A",
        "#",
    ])

    try:
        CIFFormat._write_from_dict(data, file_name)
        with open(file_name, "r") as file:
            file_text = file.read()
        assert true_text == file_text

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


def test_text_block_wrapping():

    """String values are wrapped so that each line ends with a non-whitespace character."""

    wrap_at = 10

    tests = [
        ("abcdefghij", [";abcdefghij", ";"]),
        ("abcdefghijk", [";abcdefghij", "k", ";"]),
        ("abcdefghij k", [";abcdefghij", " k", ";"]),
        ("abcdefghi jk", [";abcdefghi", " jk", ";"]),
        ("abc defghijk", [";abc defghi", "jk", ";"]),
        ("abcdefghi  ", [";abcdefghi", ";"]),
    ]

    for case, answer in tests:
        assert CIFFormat._value_into_text_block(case, wrap_at) == answer

def test_write_text_block():

    file_name = TEST_FOLDER / "test.cif"

    data = {"data_":
                {"_info":
                     {"seq": "MIKRSKKNSLALSLTADQMVSALLDAEPPILYSEYDPTRPFSEASMMGLLTNLADRELVHMINWAKRVPGFVDLTLHDQVHLLECAWLEILMIGLVWRSMEHPGKLL",
                      "lymeric": "There was a young lady from Ryde, who ate green apples and died. The apples fermented inside the lamented, and made cider inside her insides."}}}

    true_text = "\n".join([
        "data_",
        "#",
        "_info.seq",
        ";MIKRSKKNSLALSLTADQMVSALLDAEPPILYSEYDPTRPFSEASMMGLLTNLADRELVHMINWAKRVPGFVDLTLHDQV",
        "HLLECAWLEILMIGLVWRSMEHPGKLL",
        ";",
        "_info.lymeric",
        ";There was a young lady from Ryde, who ate green apples and died. The apples ferm",
        "ented inside the lamented, and made cider inside her insides.",
        ";",
        "#",
    ])

    try:
        CIFFormat._write_from_dict(data, file_name)
        with open(file_name, "r") as file:
            file_text = file.read()
        assert true_text == file_text

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


def test_write_table():

    file_name = TEST_FOLDER / "test.cif"

    data = {"data_":
                {"_info": {"name": ["A", "B", "C"],
                           "count": ["30", "2", "1"],
                           "description": ["red and bouncy",
                                           "A leafy plant in a lime-green pot, with a pair of tall, defiant white flowers",
                                           "soft and sticky"]}}}

    true_text = "\n".join([
        "data_",
        "#",
        "loop_",
        "_info.name",
        "_info.count",
        "_info.description",
        "A 30",
        '"red and bouncy"',
        "B 2",
        '"A leafy plant in a lime-green pot, with a pair of tall, defiant white flowers"',
        "C 1",
        '"soft and sticky"',
        "#"
    ])

    try:
        CIFFormat._write_from_dict(data, file_name)
        with open(file_name, "r") as file:
            file_text = file.read()
        assert true_text == file_text

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


def test_read_multi_dataset():

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "data_A",
        "#",
        "_info.item      1",
        "#",
        "data_B",
        "#",
        "_type.name      X",
        "#"
    ])

    with open(file_name, "w") as file:
        file.write(text)

    try:
        data = CIFFormat._extract_data(file_name)
    finally:
        os.remove(file_name)

    assert data == {"data_A": {"_info": {"item": "1"}},
                    "data_B": {"_type": {"name": "X"}}}


def test_write_multi_dataset():

    file_name = TEST_FOLDER / "test.cif"

    data = {"data_A":
                {"_info":
                     {"item": "1"}},
            "data_B":
                {"_type":
                     {"name": "X"}}}

    true_text = "\n".join([
        "data_A",
        "#",
        "_info.item 1",
        "#",
        "data_B",
        "#",
        "_type.name X",
        "#"
    ])

    try:
        CIFFormat._write_from_dict(data, file_name)
        with open(file_name, "r") as file:
            file_text = file.read()
        assert true_text == file_text

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


def test_full_dict_read_write():

    """Read and write are consistent - all data which can be read from an original .cif file can then be written
    in the same format, such that a subsequent read of the new file recovers identical data."""

    test_file_name = TEST_FOLDER / "test.cif"
    example_file_names = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".cif")]

    errors = []

    try:
        for file_name in example_file_names:
            original = CIFFormat._extract_data(DATA_FOLDER / file_name)
            CIFFormat._write_from_dict(original, test_file_name)
            new = CIFFormat._extract_data(test_file_name)
            assert original == new
    except AssertionError as ae:
        raise ae
    except Exception as e:
        errors.append(str(e))
    finally:
        if os.path.exists(test_file_name):
            os.remove(test_file_name)
        print(f"There were {len(errors)} other errors:\n{"\n".join(errors)}")


def test_atom_from_dict(example_atom):

    data = {
        "data_": {
            "_atom_site":
                {"group_PDB": ["ATOM"],
                 "id": ["1"],
                 "type_symbol": ["C"],
                 "label_atom_id": ["CA"],
                 "label_alt_id": ["."],
                 "label_comp_id": ["MET"],
                 "label_asym_id": ["A"],
                 "label_seq_id": ["1"],
                 "pdbx_PDB_ins_code": ["?"],
                 "Cartn_x": ["1.000"],
                 "Cartn_y": ["2.000"],
                 "Cartn_z": ["3.000"],
                 "occupancy": ["1.00"],
                 "B_iso_or_equiv": ["10.00"],
                 "pdbx_formal_charge": ["?"],
                 "auth_asym_id": ["A"],
            }
        }
    }

    assert CIFFormat._atoms_from_dict(data) == [example_atom]

def test_dict_from_atom(example_atom):

    data = {"_atom_site":
                {"group_PDB": ["ATOM"],
                 "id": ["1"],
                 "type_symbol": ["C"],
                 "label_atom_id": ["CA"],
                 "label_alt_id": ["?"],
                 "label_comp_id": ["MET"],
                 "label_asym_id": ["A"],
                 "label_seq_id": ["1"],
                 "pdbx_PDB_ins_code": ["?"],
                 "Cartn_x": ["1.0"],
                 "Cartn_y": ["2.0"],
                 "Cartn_z": ["3.0"],
                 "occupancy": ["1.0"],
                 "B_iso_or_equiv": ["10.0"],
                 "pdbx_formal_charge": ["?"],
                 "auth_asym_id": ["A"],
                 }
            }

    assert CIFFormat._atoms_to_dict([example_atom]) == data

def test_full_atom_read_write(sample_size=100):

    """Read and write, to atoms and back to file, are consistent."""

    test_filename = TEST_FOLDER / "test.cif"
    example_file_names = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".cif")]

    cif_files = random.sample(example_file_names, sample_size)

    mismatches = []
    other_errors = []
    pass_count = 0

    for filename in cif_files:
        try:
            original = CIFFormat.read_file(DATA_FOLDER / filename)
            CIFFormat.to_file(original, test_filename)
            new = CIFFormat.read_file(test_filename)
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
        print(f"There were {len(other_errors)} other errors. First ({filename}):\n{str(error)}")