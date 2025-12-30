from collections.abc import Iterable
from typing import Self

from atomflow.aspects import *
from atomflow.knowledge import *


def aspects(*__aspects: tuple[type[Aspect]] | type[Aspect]):
    def deco(cls):
        missing = [a.__name__ for a in __aspects if not isinstance(cls, a)]
        if missing:
            raise Exception(f"{cls.__name__} doesn't implement {', '.join(missing)}")
        cls.aspects = __aspects
        return cls
    return deco


class Component:
    aspects: Iterable[Aspect] | None = None

    def __repr__(self):
        values = [f"{p}={getattr(self, p)}" for p in sorted(self.get_prop_names())]
        return f"{self.__class__.__name__}({', '.join(values)})"

    def __eq__(self, other: Self):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def get_prop_names(self):
        return [k for k, v in self.__class__.__dict__.items() if isinstance(v, property)]


@aspects(NameAspect)
class NameComponent(Component):

    def __init__(self, name):
        self._name = str(name).strip()

    @property
    def name(self) -> str:
        return self._name


@aspects(ElementAspect)
class ElementComponent(Component):

    def __init__(self, element):
        self._element = str(element).strip()

    @property
    def element(self) -> str:
        return self._element


@aspects(ResNameAspect)
class ResidueComponent(Component):

    def __init__(self, resname):
        self._resname = str(resname).strip()

    @property
    def resname(self) -> str:
        return self._resname


@aspects(ResNameAspect, ResOLCAspect, ResTLCAspect, PolymerAspect)
class AAResidueComponent(Component):

    def __init__(self, res):
        res = str(res).strip()
        if olc := AA_RES_TO_SYM.get(res):
            self._tlc = res
            self._olc = olc
        elif tlc := AA_SYM_TO_RES.get(res):
            self._tlc = tlc
            self._olc = res
        else:
            raise ValueError(f"Unrecognised amino acid residue code '{res}'.")

    @property
    def res_olc(self) -> str:
        return self._olc

    @property
    def res_tlc(self) -> str:
        return self._tlc

    @property
    def resname(self) -> str:
        return self._tlc

    @property
    def polymer(self) -> str:
        return "protein"


@aspects(ResNameAspect, ResOLCAspect, PolymerAspect)
class DNAResidueComponent(Component):

    def __init__(self, res):
        res = str(res).strip()
        if olc := DNA_RES_TO_SYM.get(res):
            self._olc = olc
            self._resname = res
        elif resname := DNA_SYM_TO_RES.get(res):
            self._olc = res
            self._resname = resname
        else:
            raise ValueError(f"Unrecognised DNA residue code '{res}'.")

    @property
    def res_olc(self) -> str:
        return self._olc

    @property
    def resname(self) -> str:
        return self._resname

    @property
    def polymer(self) -> str:
        return "dna"

@aspects(ResNameAspect, ResOLCAspect, PolymerAspect)
class RNAResidueComponent(Component):

    def __init__(self, res):
        res = str(res).strip()
        if res in RNA_RES_CODES:
            self._resname = res
        else:
            raise ValueError(f"Unrecognised RNA residue code '{res}'.")

    @property
    def resname(self) -> str:
        return self._resname

    @property
    def res_olc(self) -> str:
        return self._resname

    @property
    def polymer(self) -> str:
        return "rna"

@aspects(ResIndexAspect)
class ResIndexComponent(Component):

    def __init__(self, resindex):
        self._resindex = int(resindex)

    @property
    def resindex(self) -> int:
        return self._resindex


@aspects(IndexAspect)
class IndexComponent(Component):

    def __init__(self, index):
        self._index = int(index)

    @property
    def index(self) -> int:
        return self._index


@aspects(AltLocAspect)
class AltLocComponent(Component):

    def __init__(self, altloc):
        self._altloc = str(altloc).strip()

    @property
    def altloc(self) -> str:
        return self._altloc


@aspects(ChainAspect)
class ChainComponent(Component):

    def __init__(self, chain):
        self._chain = str(chain).strip()

    @property
    def chain(self) -> str:
        return self._chain


@aspects(InsertionAspect)
class InsertionComponent(Component):

    def __init__(self, insertion):
        self._insertion = str(insertion).strip()

    @property
    def insertion(self) -> str:
        return self._insertion


@aspects(CoordinatesAspect)
class CoordinatesComponent(Component):

    def __init__(self, x, y, z):
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def z(self) -> float:
        return self._z


@aspects(OccupancyAspect)
class OccupancyComponent(Component):

    def __init__(self, occupancy):
        self._occupancy = float(occupancy)

    @property
    def occupancy(self) -> float:
        return self._occupancy


@aspects(TemperatureFactorAspect)
class TemperatureFactorComponent(Component):

    def __init__(self, temp):
        self._temp = float(temp)

    @property
    def temp(self) -> float:
        return self._temp


@aspects(ChargeAspect)
class ChargeComponent(Component):

    def __init__(self, charge):
        self._charge = str(charge).strip()

    @property
    def charge(self) -> str:
        return self._charge


@aspects(RemotenessAspect)
class RemotenessComponent(Component):

    def __init__(self, remoteness):
        self._remoteness = str(remoteness)

    @property
    def remoteness(self) -> str:
        return self._remoteness


@aspects(BranchAspect)
class BranchComponent(Component):

    def __init__(self, branch):
        self._branch = str(branch)

    @property
    def branch(self) -> str:
        return self._branch


@aspects(PositionAspect)
class PositionComponent(Component):

    def __init__(self, position):
        self._position = str(position).strip()

    @property
    def position(self) -> str:
        return self._position


@aspects(PolymerAspect)
class PolymerComponent(Component):

    def __init__(self, polymer):
        self._polymer = str(polymer).strip()

    @property
    def polymer(self) -> str:
        return self._polymer


@aspects(EntityAspect)
class EntityComponent(Component):

    def __init__(self, entity):
        self._entity = str(entity).strip()

    @property
    def entity(self) -> str:
        return self._entity


if __name__ == '__main__':
    pass