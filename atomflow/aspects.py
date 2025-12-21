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

if __name__ == '__main__':
    pass