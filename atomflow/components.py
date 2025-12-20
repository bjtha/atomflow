from collections.abc import Iterable
from aspects import NameAspect, ElementAspect, ResNameAspect, Aspect

def aspects(*__aspects):
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
        values = [f"{asp.keyword}={getattr(self, asp.keyword)}" for asp in self.aspects]
        return f"{self.__class__.__name__}({', '.join(values)})"

@aspects(NameAspect)
class NameComponent(Component):

    def __init__(self, name):
        self._name = str(name)

    @property
    def name(self) -> str:
        return self._name

@aspects(ResNameAspect)
class ResNameComponent(Component):

    def __init__(self, resname):
        self._resname = str(resname)

    @property
    def resname(self) -> str:
        return self._resname


if __name__ == '__main__':
    res = ResNameComponent("Met")
    print(res)