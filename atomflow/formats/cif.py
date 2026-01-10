import pathlib
from collections import defaultdict
import os
from typing import Iterable

from atomflow.aspects import *
from atomflow.atom import Atom
from atomflow.formats import Format

class CIFFormat(Format):

    recipe = {
        "and": [
            IndexAspect,
            AltLocAspect,
            ChainAspect,
            NameAspect,
            ResNameAspect,
            EntityAspect,
            ResIndexAspect,
            ElementAspect,
        ]
    }

    extensions = (".cif", ".mmcif")

    @classmethod
    def read_file(cls, path: str | os.PathLike) -> list[Atom]:

        tables = cls._extract_tables(path)
        entities = tables["_entity"]



        return []

    @classmethod
    def to_file(cls, atoms: Iterable[Atom], path: str | os.PathLike) -> None:
        pass

    @staticmethod
    def _split_line(line: str) -> list[str]:

        """Splits line by whitespace, except within single quote marks.

        >>> ln = "foo 'hello world'\tbar"
        >>> assert CIFFormat._split_line(ln) == ["foo", "hello world", "bar"]
        """

        parts = []
        chars = ""
        quote = False

        for char in line:
            if char == "'":
                quote = not quote
                continue
            elif char == " ":
                if not chars:
                    # Skip consecutive whitespace
                    continue
                if not quote:
                    # If outside of quote marks, treat the space as a splitting point
                    parts.append(chars)
                    chars = ''
                    continue
            chars += char

        # Add the final word
        parts.append(chars)

        return parts

    @classmethod
    def _extract_tables(cls, path: str | os.PathLike) -> dict:

        """Reads only the table information from a cif file."""

        with open(path, "r") as file:
            lines = (ln.strip() for ln in file.readlines())

        tables = defaultdict(dict)
        in_table = False
        cat = None
        values = []
        num_cols = 0

        for line in lines:

            if line == "#":
                in_table = False

            elif line == "loop_":
                in_table = True

            elif in_table:
                if line.startswith("_"):
                    cat, field = line.split(".")
                    tables[cat][field] = []
                    num_cols = len(tables[cat])
                else:
                    values += cls._split_line(line)
                    if len(values) < num_cols:
                        # Table rows can run over multiple lines. If the number of values on this line is less
                        # than the expected number of fields, roll the values over to the next line.
                        continue
                    for field, value in zip(tables[cat], values, strict=True):
                        tables[cat][field].append(value)
                    values = []

        return tables

    @classmethod
    def _get_row_by_id(cls, table: dict[str, list], id_) -> dict:

        """Returns the row in the table which matches the given ID. Assumes that the table has a column
        named 'id'."""

        try:
            id_col = table["id"]
        except KeyError:
            raise ValueError("Table has no ID column")

        id_ = str(id_)
        if id_col.count(id_) > 1:
            raise ValueError(f"More than one row in ID column with ID {id_}\n{id_col}")

        row_num = id_col.index(id_)
        return {k: v[row_num] for k, v in table.items()}


if __name__ == '__main__':
    CIFFormat.read_file("../../tests/data/cif/1A52.cif")
