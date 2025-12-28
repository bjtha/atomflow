from atomflow.components import *
from atomflow.aspects import *
from atomflow.atom import Atom


class PDBFormat:

    recipe = {
        ProteinAspect,
        IndexAspect,
        ElementAspect,
        ResNameAspect,
        ChainAspect,
        ResIndexAspect,
        CoordinatesAspect,
    }

    @staticmethod
    def atom_from_line(line):

        record_type = line[:6].strip()  # Left-justified
        if record_type not in ("ATOM", "HETATM"):
            return

        components = [
            ProteinComponent(True if record_type == "ATOM" else False),
            IndexComponent(line[6:11]),
            ResNameComponent(line[17:20].strip()),
            ChainComponent(line[21:22].strip()),
            ResIndexComponent(line[22:26]),
            CoordinatesComponent(line[30:38], line[38:46], line[46:54]),
            ElementComponent(line[76:78].strip()),
        ]

        # Optional fields
        if altloc := line[16:17].strip():
            components.append(AltLocComponent(altloc))

        if insertion := line[26:27].strip():
            components.append(InsertionComponent(insertion))

        if occupancy := line[54:60].strip():
            components.append(OccupancyComponent(occupancy))

        if b_factor := line[60:66].strip():
            components.append(TemperatureFactorComponent(b_factor))

        if charge := line[78:80].strip():
            components.append(ChargeComponent(charge))

        name_field = line[12:16]
        components.append(PDBNameFieldComponent(name_field))

        return Atom(*components)

    @classmethod
    def line_from_atom(cls, atom: Atom):

        missing = [asp for asp in cls.recipe if not atom.implements(asp)]
        if missing:
            raise Exception(f"Could not create PDB line from {atom}")

        record_type = "ATOM" if atom.protein else "HETATM"
        atom_index = atom.index
        element = atom.element
        altloc = atom.altloc if atom.implements(AltLocAspect) else ''
        resname = atom.resname
        chain = atom.chain
        resindex = atom.resindex
        insertion = atom.insertion if atom.implements(InsertionAspect) else ''
        x_coord = f"{atom.x:.3f}"
        y_coord = f"{atom.y:.3f}"
        z_coord = f"{atom.z:.3f}"
        occupancy = f"{atom.occupancy:.2f}" if atom.implements(OccupancyAspect) else ''
        b_factor = f"{atom.temp:.2f}" if atom.implements(TemperatureFactorAspect) else ''
        charge = atom.charge if atom.implements(ChargeAspect) else ''
        _ = ' '

        # If the atom has the aspects needed to make a name field (element & position), build it
        if all(atom.implements(a) for a in (ElementAspect, RemotenessAspect, BranchAspect)):
            name_field = f"{atom.element: >2}{atom.remoteness :>1}{atom.branch :>1}"

        # Alternatively, if the atom has a stored PDB name field, use that
        elif atom.has(PDBNameFieldComponent):
            name_field = atom.name_field

        # Lastly, default to just using the element
        else:
            name_field = f"{atom.element: >2}  "

        line = \
            f"{record_type: <6}{atom_index: >5}{_}{name_field}{altloc: >1}{resname: >3}{_}{chain}"\
            f"{resindex: >4}{insertion: >1}{_: >3}"\
            f"{x_coord: >8}{y_coord: >8}{z_coord: >8}{occupancy: >6}{b_factor: >6}{_: >10}"\
            f"{element :>2}{charge :<2}"

        return line

if __name__ == '__main__':
    line = "ATOM   1283  OD2 ASP B  68      20.233 -23.581  28.711  1.00 76.04           O1-"
    atom = PDBFormat.atom_from_line(line)

    print(atom.name_field)

    converted = PDBFormat.line_from_atom(atom)

    print(line)
    print(converted)
