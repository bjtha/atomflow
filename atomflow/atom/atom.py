from typing import Self

from atomflow.aspects import Aspect
from atomflow.components import Component, NameComponent, ResNameComponent

class Atom:
    def __init__(self, *components):
        self._by_aspect: dict[Aspect: list[Component]] = {}
        self._by_keyword: dict[str: list[Component]] = {}
        for c in components:
            self.add(c)

    def __getattr__(self, item):
        if comps := self._by_keyword.get(item):
            return getattr(comps[-1], item)
        raise AttributeError(f"Atom has no data for '{item}'")

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __format__(self, format_spec):

        if not format_spec:
            return f"{self:s}"

        elif format_spec == 'l':
            cmp_vals = [str(cmps[-1]) for cmps in sorted(self._by_aspect.values())]
            cmp_lines = "\n\t".join(cmp_vals)
            return f"Atom(\n\t{cmp_lines}\n\t)"

        elif format_spec == 's':
            vals = [f"{kw}={self[kw]}" for kw in sorted(self._by_keyword)]
            return f"Atom({', '.join(vals)})"

        else:
            raise ValueError(f"Unknown format specifier '{format_spec}' for Atom.")

    def __repr__(self):
        return f"{self}"

    def __eq__(self, other: Self):
        return str(self) == str(other)

    def add(self, comp: Component):
        for asp in comp.aspects:
            self._by_aspect.setdefault(asp, []).append(comp)
        for prop in comp.get_prop_names():
            self._by_keyword.setdefault(prop, []).append(comp)

    def implements(self, asp: Aspect):
        return asp in self._by_aspect

    def has(self, cmp_type: type[Component]):
        return any(isinstance(cmps[-1], cmp_type) for cmps in self._by_aspect.values())

if __name__ == '__main__':
    atom = Atom()
    name = NameComponent("CA")
    atom.add(name)
    print(atom.name)

    resn = ResNameComponent("MET")
    atom.add(resn)
    print(atom.resname)
