from typing import Protocol, runtime_checkable

def attribute(kw):
    def deco(cls):
        setattr(cls, kw, lambda: None)
        cls.keyword = kw
        return cls
    return deco

@runtime_checkable
class Aspect(Protocol): pass

@runtime_checkable
@attribute("name")
class NameAspect(Aspect, Protocol): pass

@runtime_checkable
@attribute("element")
class ElementAspect(Aspect, Protocol): pass

@runtime_checkable
@attribute("resname")
class ResNameAspect(Aspect, Protocol): pass

if __name__ == '__main__':
    pass