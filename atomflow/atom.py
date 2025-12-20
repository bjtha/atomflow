from aspects import Aspect
from components import Component, NameComponent, ResNameComponent

class Atom:
    def __init__(self):
        self._components: dict[Aspect: list[Component]] = {}

    def __getattr__(self, item):
        for cmps in self._components.values():
            if att := getattr(cmps[-1], item, None):
                return att
        raise AttributeError(f"Atom has no data for '{item}'")

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __repr__(self):
        cmp_vals = [str(cmps[-1]) for cmps in self._components.values()]
        cmp_lines = "\n\t".join(cmp_vals)
        return f"Atom(\n\t{cmp_lines}\n\t)"

    def add(self, comp: Component):
        for asp in comp.aspects:
            self._components.setdefault(asp, []).append(comp)

    def implements(self, asp: Aspect):
        return asp in self._components


if __name__ == '__main__':
    atom = Atom()
    name = NameComponent("CA")
    atom.add(name)
    print(atom.name)

    resn = ResNameComponent("MET")
    atom.add(resn)
    print(atom.resname)

    print(atom)
