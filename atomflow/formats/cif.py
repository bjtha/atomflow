from collections import defaultdict
import os
from typing import Iterable

from atomflow.components import *
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

    field_cmp_mapping = {
        "id": IndexComponent,
        "label_alt_id": AltLocComponent,
        "label_asym_id": ChainComponent,
        "label_atom_id": NameComponent,
        "label_seq_id": ResIndexComponent,
        "type_symbol": ElementComponent,
        "Cartn_x": CoordXComponent,
        "Cartn_y": CoordYComponent,
        "Cartn_z": CoordZComponent,
        "occupancy": OccupancyComponent,
        "pdbx_PDB_ins_code": InsertionComponent,
        "B_iso_or_equiv": TemperatureFactorComponent,
        "pdbx_formal_charge": FormalChargeComponent,
    }

    @classmethod
    def read_file(cls, path: str | os.PathLike) -> list[Atom]:

        tables = cls._extract_data(path, names=("_entity", "_atom_site"))

        entity_table = tables["_entity"]
        atom_table = tables["_atom_site"]

        num_rows = len(atom_table["id"])

        atoms = []

        for atom_i in range(num_rows):

            cmps = []

            values = [col[atom_i] for col in atom_table.values()]
            for field_name, value in zip(atom_table, values):

                # Skip unknown/placeholder values
                if value in "?.":
                    continue

                # For cases with simple 1:1 mapping between data item (field) and component type
                elif field_name in cls.field_cmp_mapping:
                    cmp_type = cls.field_cmp_mapping[field_name]
                    cmps.append(cmp_type(value))

                elif field_name == "label_comp_id":
                    if value in AA_RES_TO_SYM:
                        cmps.append(AAResidueComponent(value))
                    elif value in DNA_RES_TO_SYM:
                        cmps.append(DNAResidueComponent(value))
                    elif value in RNA_RES_CODES:
                        cmps.append(RNAResidueComponent(value))
                    else:
                        cmps.append(ResidueComponent(value))

                # Get entity name from table
                elif field_name == "label_entity_id":
                    entity_row = cls._get_row_by_id(entity_table, int(value))
                    entity_name = entity_row["pdbx_description"]
                    cmps.append(EntityComponent(entity_name))

            atoms.append(Atom(*cmps))

        return atoms

    @classmethod
    def to_file(cls, atoms: Iterable[Atom], path: str | os.PathLike) -> None:
        pass

    @staticmethod
    def _split_line(line: str) -> list[str]:

        """Splits line by whitespace, except within single or double quote marks.

        >>> ln = "foo 'hello world'\tbar"
        >>> assert CIFFormat._split_line(ln) == ["foo", "hello world", "bar"]
        """

        parts = []
        chars = ""
        quote = []

        for char in line:
            if char in ('"', "'"):
                if not quote:
                    quote.append(char)
                    continue
                elif char in quote:
                    quote.remove(char)
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
    def _extract_data(cls, path: str | os.PathLike, names: None | Iterable[str] = None) -> dict:

        """Reads the information from a cif file into a dict. Optionally only extract categories with given names."""

        with open(path, "r") as file:
            lines = (ln.strip() for ln in file.readlines())

        tables = {}
        in_table = False
        in_text_block = False
        cat = None
        field = None
        buffer = []
        num_cols = 0

        for line in lines:

            if line == "#":
                in_table = False

            elif line == "loop_":
                in_table = True

            elif in_table:
                if line.startswith("_"):
                    # This line describes a field in the table
                    cat, field = line.split(".")

                    # If 'names' arg has been given, and this category isn't in it, skip the table.
                    if names and cat not in names:
                        in_table = False
                        continue

                    # Add the field to the table
                    tables.setdefault(cat, dict())[field] = []
                    num_cols = len(tables[cat])
                else:
                    # This line has data from the table
                    buffer += cls._split_line(line)
                    if len(buffer) < num_cols:
                        # Table rows can run over multiple lines. If the number of values on this line is less
                        # than the expected number of fields, aggregate with values from the next line.
                        continue
                    for field, value in zip(tables[cat], buffer, strict=True):
                        tables[cat][field].append(value)
                    buffer = []

            elif line.startswith("_"):
                # This line contains a non-tabular data item

                # If this represents the end of a text block, deal with the collected data.
                if in_text_block:
                    if not buffer:
                        raise ValueError(f"Expected text block, got: '{line}'")
                    item = "".join(buffer)
                    # category and field names will still be as they were when the text block was discovered
                    tables.setdefault(cat, dict())[field] = item
                    in_text_block = False
                    buffer = []

                parts = cls._split_line(line)
                cat, field = parts[0].split(".")

                # If 'names' arg has been given, and this category isn't in it, skip the item.
                if names and cat not in names:
                    continue

                num_parts = len(parts)
                if num_parts == 1:
                    # If only an identifier, then a multi-line text block is expected to follow.
                    in_text_block = True
                elif num_parts == 2:
                    # Otherwise, the second part of the line is the data for this field.
                    tables.setdefault(cat, dict())[field] = parts[1]
                else:
                    raise ValueError(f"Too many data items on line: {line}")

            elif in_text_block:
                # This line is part of a text block.
                buffer.append(line.lstrip(";").strip())

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
    data = CIFFormat._extract_data("../../tests/data/cif/1A52.cif", names=("_pdbx_entity_nonpoly",))
    print(data)