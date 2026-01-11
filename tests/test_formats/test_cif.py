import os
import pathlib

import pytest

from atomflow.formats import CIFFormat

TEST_FOLDER = pathlib.Path("tests/test_formats")


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