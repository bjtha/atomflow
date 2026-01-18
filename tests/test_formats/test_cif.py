import os
import pathlib

import pytest

from atomflow.formats import CIFFormat

TEST_FOLDER = pathlib.Path("tests/test_formats")
DATA_FOLDER = pathlib.Path("tests/data/cif")

def test_extract_data_items():

    """Single data items and text blocks are extracted and compiled into a dict."""

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "#",
        "_data.item      1",
        "_data.name      A",
        "_data.text",
        ";The quick brown",
        " fox jumped over",
        " the lazy dog.",
        ";",
        "_data.cost     10",
        "_data.title",
        ";",
        "Pride and Prejudice",
        ";",
        "_data.lyric",
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

    assert data == {"_data": {"item": "1",
                              "name": "A",
                              "text": "The quick brown fox jumped over the lazy dog.",
                              "cost": "10",
                              "title": "Pride and Prejudice",
                              "lyric": "I love you like a rose loves rainwater"}}

def test_extract_data_item_failures():

    # Read fails if text block is interrupted.

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "#",
        "_data.text",
        "; A lady sat upon a bridge,",
        "#",  # Block ended without a ';'
    ])

    with open(file_name, "w") as file:
        file.write(text)

    with pytest.raises(ValueError):
        CIFFormat._extract_data(file_name)
    os.remove(file_name)

    # It also fails if a data item has more than one value.

    text = "\n".join([
        "#",
        "_data.list   1   2",
        "#"
    ])

    with open(file_name, "w") as file:
        file.write(text)

    with pytest.raises(ValueError):
        CIFFormat._extract_data(file_name)
    os.remove(file_name)

def test_extract_data_tables():

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "#",
        "loop_",
        "_data.name",
        "_data.count",
        "_data.description",
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

    assert data == {"_data": {"name": ["A", "B"],
                              "count": ["3", "2"],
                              "description": ["red and bouncy", "soft and sticky"]}}


def test_extract_data_selection():

    """If provided, only named data categories are extracted."""

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "#",
        "_data.item      1",
        "_data.text",
        ";The quick brown",
        " fox jumped over",
        " the lazy dog.",
        ";",
        "#",
        "_info.name      A",
        "#"
    ])

    with open(file_name, "w") as file:
        file.write(text)

    try:
        data = CIFFormat._extract_data(file_name, categories=("_info",))
    finally:
        os.remove(file_name)

    assert data == {"_info": {"name": "A"}}


def test_extract_data_table_failures():

    # Read fails if there's a mismatch between the number of declared fields and the number of data items

    file_name = TEST_FOLDER / "test.cif"

    text = "\n".join([
        "#",
        "loop_",
        "_data.name",
        "_data.count", # Two fields
        "A 3 'red and bouncy'",
        "B 2 'soft and sticky'", # Three values
        "#"
    ])

    with open(file_name, "w") as file:
        file.write(text)

    with pytest.raises(ValueError):
        CIFFormat._extract_data(file_name)
    os.remove(file_name)


def test_write_data_items():

    file_name = TEST_FOLDER / "test.cif"

    data = {"_data": {"item": "1",
                      "name": "A"}}

    true_text = "\n".join([
        "data_",
        "#",
        "_data.item 1",
        "_data.name A",
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

    data = {"_data": {"seq": "MIKRSKKNSLALSLTADQMVSALLDAEPPILYSEYDPTRPFSEASMMGLLTNLADRELVHMINWAKRVPGFVDLTLHDQVHLLECAWLEILMIGLVWRSMEHPGKLL",
                      "lymeric": "There was a young lady from Ryde, who ate green apples and died. The apples fermented inside the lamented, and made cider inside her insides."}}

    true_text = "\n".join([
        "data_",
        "#",
        "_data.seq",
        ";MIKRSKKNSLALSLTADQMVSALLDAEPPILYSEYDPTRPFSEASMMGLLTNLADRELVHMINWAKRVPGFVDLTLHDQV",
        "HLLECAWLEILMIGLVWRSMEHPGKLL",
        ";",
        "_data.lymeric",
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

    data = {"_data": {"name": ["A", "B", "C"],
                      "count": ["30", "2", "1"],
                      "description": ["red and bouncy",
                                      "A leafy plant in a lime-green pot, with a pair of tall, defiant white flowers",
                                      "soft and sticky"]}}

    true_text = "\n".join([
        "data_",
        "#",
        "loop_",
        "_data.name",
        "_data.count",
        "_data.description",
        "A 30",
        "'red and bouncy'",
        "B 2",
        "'A leafy plant in a lime-green pot, with a pair of tall, defiant white flowers'",
        "C 1",
        "'soft and sticky'",
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
