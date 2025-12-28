from atomflow.components import *
from atomflow.aspects import *
from atomflow.atom import Atom

AA_RES_CODES = {
    "ALA": "A", "CYS": "C", "ASP": "D", "GLU": "E", "PHE": "F",
    "GLY": "G", "HIS": "H", "ILE": "I", "LYS": "K", "LEU": "L",
    "MET": "M", "ASN": "N", "PRO": "P", "GLN": "Q", "ARG": "R",
    "SER": "S", "THR": "T", "VAL": "V", "TRP": "W", "TYR": "Y",
}
DNA_RES_CODES = {"DA", "DG", "DT", "DC"}
RNA_RES_CODES = {"A", "G", "U", "C"}

class PDBFormat:

    recipe = {
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
            IndexComponent(line[6:11]),
            NameComponent(line[12:16].strip()),
            ResNameComponent(line[17:20].strip()),
            ChainComponent(line[21:22].strip()),
            ResIndexComponent(line[22:26]),
            CoordinatesComponent(line[30:38], line[38:46], line[46:54]),
            ElementComponent(line[76:78].strip()),
        ]

        # Extract position part from name
        name = line[12:16].strip()
        elem = line[76:78].strip()
        position = name[len(elem):]
        components.append(PositionComponent(position))

        # Determine polymer membership from residue name
        res_name = line[17:20].strip()
        if res_name in AA_RES_CODES:
            components.append(PolymerComponent("protein"))
        elif res_name in DNA_RES_CODES:
            components.append(PolymerComponent("dna"))
        elif res_name in RNA_RES_CODES:
            components.append(PolymerComponent("rna"))

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

        return Atom(*components)

    @classmethod
    def line_from_atom(cls, atom: Atom):

        missing = [asp for asp in cls.recipe if not atom.implements(asp)]
        if missing:
            raise Exception(f"Could not create PDB line from {atom}")

        record_type = "ATOM" if atom.implements(PolymerAspect) else "HETATM"

        # If the atom has the aspects needed to make a name field (element & position), build it
        if all(atom.implements(a) for a in (ElementAspect, PositionAspect)):
            name_field = f"{atom.element: >2}{atom.position: <2}"
            # Hydrogen positions sometimes spill over on the right
            if len(name_field) > 4:
                name_field = name_field.strip()
        else:
            name_field = f"{atom.element: >2}  "

        altloc = atom.altloc if atom.implements(AltLocAspect) else ''
        ins = atom.insertion if atom.implements(InsertionAspect) else ''
        occ = atom.occupancy if atom.implements(OccupancyAspect) else ''
        b = atom.temp if atom.implements(TemperatureFactorAspect) else ''
        charge = atom.charge if atom.implements(ChargeAspect) else ''
        _ = ' '

        return \
            f"{record_type: <6}{atom.index: >5}{_}{name_field}{altloc: >1}"\
            f"{atom.resname: >3}{_}{atom.chain}{atom.resindex: >4}{ins: >1}{_: >3}"\
            f"{atom.x: >8.3f}{atom.y: >8.3f}{atom.z: >8.3f}{occ: >6.2f}{b: >6.2f}{_: >10}"\
            f"{atom.element :>2}{charge :<2}"


if __name__ == '__main__':
    line = "ATOM     97 HH12 ARG A   5      -0.465 -17.875  -4.318  1.00  0.00           H  "
    atom = PDBFormat.atom_from_line(line)

    print(atom.position)

    converted = PDBFormat.line_from_atom(atom)

    print(line)
    print(converted)
