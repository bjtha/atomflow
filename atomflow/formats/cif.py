import os
from typing import Iterable

from atomflow.components import *
from atomflow.atom import Atom
from atomflow.formats import Format

COLUMN_PADDING = 1
WRAP_AT = 80

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

        tables = cls._extract_data(path, categories=("_entity", "_atom_site"))

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
    def _extract_data(cls, path: str | os.PathLike, categories: None | Iterable[str] = None) -> dict:

        """Reads the information from a cif file into a dict. Optionally only extract categories with given names."""

        with open(path, "r") as file:
            lines = (ln.rstrip() for ln in file.readlines())

        tables = {}
        in_table = False
        in_text_block = False
        cat = None
        field = None
        buffer = []
        num_cols = 0

        for line in lines:
            if in_text_block and line[0] in "#_":
                raise ValueError(f"Unexpected end of text block on line:\n{line}")

            if line.startswith("#"):
                in_table = False

            elif line.startswith("loop_"):
                in_table = True

            elif line.startswith("_"):
                # This line declares either a data item, or a table field.
                parts = cls._split_line(line)
                cat, field = parts[0].split(".")
                num_parts = len(parts)
                # If 'categories' arg has been given, and this label's category isn't in it, skip the item / table.
                if categories and cat not in categories:
                    in_table = False
                elif in_table:
                    tables.setdefault(cat, dict())[field] = []
                    num_cols = len(tables[cat])
                # Otherwise, treat as a data item
                elif num_parts == 2:
                    tables.setdefault(cat, dict())[field] = parts[1]
                elif num_parts > 2:
                    raise ValueError(f"Too many data items on line, expected 2 or fewer:\n{line}")

            # Skip text block lines and table rows if last declared category not selected for extraction
            elif categories and cat not in categories:
                continue

            elif line.startswith(";"):
                # This line is the beginning or end of a text block.
                # Tell the difference by checking if lines have been accumulated.
                if buffer:
                    item = "".join(buffer)
                    tables.setdefault(cat, dict())[field] = item
                    in_text_block = False
                    buffer = []
                else:
                    buffer.append(line.lstrip(";").strip())
                    in_text_block = True

            elif in_table:
                buffer += cls._split_line(line)
                if len(buffer) < num_cols:
                    # Table rows can run over multiple lines. If the number of values is less
                    # than the number of fields, roll them over to the next line.
                    continue
                for field, value in zip(tables[cat], buffer, strict=True):
                    tables[cat][field].append(value)
                buffer = []

            elif in_text_block:
                buffer.append(line)

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

    @classmethod
    def _write_from_dict(cls, data: dict, path: str | os.PathLike) -> None:

        lines = ["data_", "#"]

        for category in data:
            fields = data[category]
            labels = [category + "." + f for f in fields]

            if all(isinstance(v, str) for v in fields.values()):
                # This category contains single label:value pairs
                col_width = max(map(len, labels)) + COLUMN_PADDING
                for item, value in fields.items():
                    label = category + "." + item
                    if col_width + len(value) > WRAP_AT:
                        lines.extend([label] + cls._value_into_text_block(value, WRAP_AT))
                    else:
                        formatted = "'" + value + "'" if " " in value else value
                        lines.append(f"{label: <{col_width}}{formatted}")

            elif all(isinstance(v, list) for v in fields.values()):
                # This category is a table
                lines.append("loop_")
                columns = []
                widths = []
                for item, values in data[category].items():
                    label = category + "." + item
                    lines.append(label)
                    col = []
                    max_width = 0
                    for v in values:
                        # Surround strings containing spaces with quotes
                        formatted = "'" + v + "'" if " " in v else v
                        col.append(formatted)
                        max_width = max(max_width, len(formatted))
                    widths.append(max_width)
                    columns.append(col)

                for row in zip(*columns):
                    line = ""
                    for width, value in zip(widths, row):
                        padded = f"{value: <{width + COLUMN_PADDING}}"
                        if len(line) + len(padded) > WRAP_AT:
                            lines.append(line.rstrip())
                            line = padded
                        else:
                            line += padded
                    lines.append(line.rstrip())

            else:
                raise ValueError(f"Unexpected field value types. Must be <str> or <list>.")
            lines.append("#")

        with open(path, "w") as file:
            file.write("\n".join(lines))

    @staticmethod
    def _value_into_text_block(value: str, wrap_at) -> list[str]:

        """Wraps string value into a text block of width 'wrap_at', ensuring to never
        end a line with whitespace. Leading and tailing whitespace is ignored."""

        value = value.strip()
        whitespace = {" ", "\t"}
        text_block_lines = []
        start = 0
        break_ = 0
        i = 0

        while i < len(value):
            if i-start == wrap_at:
                if start == break_:
                    raise ValueError("Line is only whitespace")
                # Increment break_ by 1 so that slicing includes the non-whitespace character it stopped at
                break_ = break_+1
                text_block_lines.append(value[start:break_])
                i = break_
                start = break_
            if value[i] not in whitespace:
                # Track the position of the last non-whitespace character
                break_ = i
            i += 1
        # When cursor reaches the end, add the final set of characters
        text_block_lines.append(value[start:i])

        text_block_lines[0] = ";" + text_block_lines[0]
        text_block_lines.append(";")
        return text_block_lines

if __name__ == '__main__':
    pass