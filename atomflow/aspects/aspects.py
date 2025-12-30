from typing import Protocol, runtime_checkable

@runtime_checkable
class Aspect(Protocol): pass


@runtime_checkable
class NameAspect(Aspect, Protocol):

    @property
    def name(self) -> str: pass


@runtime_checkable
class ElementAspect(Aspect, Protocol):

    @property
    def element(self) -> str: pass


@runtime_checkable
class ResNameAspect(Aspect, Protocol):

    @property
    def resname(self) -> str: pass


@runtime_checkable
class ResOLCAspect(Aspect, Protocol):

    @property
    def res_olc(self) -> str: pass


@runtime_checkable
class ResTLCAspect(Aspect, Protocol):

    @property
    def res_tlc(self) -> str: pass


@runtime_checkable
class ResIndexAspect(Aspect, Protocol):

    @property
    def resindex(self) -> float: pass


@runtime_checkable
class PolymerAspect(Aspect, Protocol):

    @property
    def polymer(self) -> str: pass


@runtime_checkable
class IndexAspect(Aspect, Protocol):

    @property
    def index(self) -> int: pass


@runtime_checkable
class RemotenessAspect(Aspect, Protocol):

    @property
    def remoteness(self) -> str: pass


@runtime_checkable
class AltLocAspect(Aspect, Protocol):

    @property
    def altloc(self) -> str: pass


@runtime_checkable
class ChainAspect(Aspect, Protocol):

    @property
    def chain(self) -> str: pass


@runtime_checkable
class InsertionAspect(Aspect, Protocol):

    @property
    def insertion(self) -> str: pass


@runtime_checkable
class CoordinatesAspect(Aspect, Protocol):

    @property
    def x(self) -> float: pass

    @property
    def y(self) -> float: pass

    @property
    def z(self) -> float: pass


@runtime_checkable
class OccupancyAspect(Aspect, Protocol):

    @property
    def occupancy(self) -> float: pass


@runtime_checkable
class TemperatureFactorAspect(Aspect, Protocol):

    @property
    def temp(self) -> float: pass


@runtime_checkable
class ChargeAspect(Aspect, Protocol):

    @property
    def charge(self) -> int: pass


@runtime_checkable
class BranchAspect(Aspect, Protocol):

    @property
    def branch(self) -> str: pass


@runtime_checkable
class BackboneAspect(Aspect, Protocol):

    @property
    def backbone(self) -> bool: pass


@runtime_checkable
class NameFieldAspect(Aspect, Protocol):

    @property
    def name_field(self) -> str: pass


@runtime_checkable
class PositionAspect(Aspect, Protocol):

    @property
    def position(self) -> str: pass


@runtime_checkable
class EntityAspect(Aspect, Protocol):

    @property
    def entity(self) -> str: pass