from typing import Self, Iterable, Mapping

from atomflow.aspects import Aspect
from atomflow.components import Component

class Atom:
    def __init__(self, *components: Component | Iterable[Component]):
        self._by_aspect: dict[Aspect: list[Component]] = {}
        self._by_keyword: dict[str: list[Component]] = {}
        for c in components:
            self.add(c)

    def __getattr__(self, item):

        """
        Retrieves data matching the aspect keyword from the latest added component.

        >>> from atomflow.components import NameComponent
        >>> atom = Atom(NameComponent("CA"))
        >>> assert atom.name == "CA"
        >>> atom.add(NameComponent("N"))
        >>> assert atom.name == "N"

        Raises AtrributeError if keyword doesn't exist in internal dict.

        >>> atom.tree
        Traceback (most recent call last):
            ...
        AttributeError: Atom has no data for 'tree'
        """

        if comps := self._by_keyword.get(item):
            return getattr(comps[-1], item)
        raise AttributeError(f"Atom has no data for '{item}'")

    def __getitem__(self, item):

        """
        Refers to __getattr__, for accessing dynamically with strings.

        >>> from atomflow.components import NameComponent
        >>> atom = Atom(NameComponent("CA"))
        >>> assert atom["name"] == "CA"
        """

        return self.__getattr__(item)

    def __format__(self, format_spec):

        r"""
        Default short (s) format only properties and their values in alphabetical order:

        >>> from atomflow.components import NameComponent, IndexComponent
        >>> atom = Atom(NameComponent("CA"), IndexComponent(1))
        >>> assert str(atom) == f"{atom:s}" == "Atom(index=1, name=CA)"

        Long (l) format lists components:

        >>> assert f"{atom:l}" == "Atom(\n\tIndexComponent(index=1),\n\tNameComponent(name=CA)\n)"

        Which prints as:
        Atom(
            IndexComponent(index=1),
            NameComponent(name=CA)
        )
        """

        if not format_spec:
            return f"{self:s}"

        elif format_spec == 'l':
            cmp_vals = [str(cmps[-1]) for cmps in sorted(self._by_aspect.values())]
            cmp_lines = ",\n\t".join(cmp_vals)
            return f"Atom(\n\t{cmp_lines}\n)"

        elif format_spec == 's':
            vals = [f"{kw}={self[kw]}" for kw in sorted(self._by_keyword)]
            return f"Atom({', '.join(vals)})"

        else:
            raise ValueError(f"Unknown format code '{format_spec}' for object of type 'Atom'.")

    def __repr__(self):
        return f"{self}"

    def __eq__(self, other: Self):
        return str(self) == str(other)

    def __lt__(self, other: Self):
        return str(self) < str(other)

    def add(self, cmp: Component) -> None:

        """
        Adds component to internal dicts, indexing by aspect object and aspect name.

        >>> from atomflow.aspects import NameAspect
        >>> from atomflow.components import NameComponent
        >>> atom = Atom()
        >>> component = NameComponent("CA")
        >>> atom.add(component)
        >>> assert atom._by_aspect == {NameAspect: [component]}
        >>> assert atom._by_keyword == {"name": [component]}

        Can be called during initialisation:
        >>> atom = Atom(component)
        >>> assert atom._by_aspect == {NameAspect: [component]}
        """

        for asp in cmp.aspects:
            self._by_aspect.setdefault(asp, []).append(cmp)
        for prop in cmp.get_property_names():
            self._by_keyword.setdefault(prop, []).append(cmp)

    def implements(self, item: Aspect | Mapping) -> bool:

        """
        Returns True if Atom implements given aspect or recipe structure.

        >>> from atomflow.components import NameComponent
        >>> from atomflow.aspects import NameAspect, ElementAspect, PositionAspect
        >>> atom = Atom(NameComponent("CA"))
        >>> assert atom.implements(NameAspect) == True
        >>> assert atom.implements(ElementAspect) == False

        Recipes are expected as branching mappings, with each key as the logical operator for
        the following iterable.

        >>> recipe = {"or" : [NameAspect, {"and": [ElementAspect, PositionAspect]}]}
        >>> assert atom.implements(recipe) == True
        >>> recipe = {"and": [PositionAspect, {"or": [NameAspect, ElementAspect]}]}
        >>> assert atom.implements(recipe) == False

        :param item: Aspect or Mapping to test implementation of
        :return: bool
        """

        if isinstance(item, Aspect):
            return item in self._by_aspect

        elif isinstance(item, Mapping):
            for key in item:
                if key == "or":
                    if not any(self.implements(x) for x in item[key]):
                        return False
                elif key == "and":
                    if not all(self.implements(x) for x in item[key]):
                        return False
                else:
                    raise KeyError(f"Unknown operator: '{key}'")
        else:
            return False

        return True

if __name__ == '__main__':
    pass