from collections import deque
from collections.abc import Iterable

from atomflow.atom import Atom
from atomflow.components import NameComponent, ResidueComponent

END = object()


class AtomIterator:

    """
    Base iterator. Converts a list of Atoms into an iterator where each atom is in its own group.

    >>> from atomflow.atom import Atom
    >>> from atomflow.components import NameComponent, ResidueComponent, IndexComponent

    >>> atom_a = Atom(NameComponent("A"), ResidueComponent("X"), IndexComponent(3))
    >>> atom_b = Atom(NameComponent("B"), ResidueComponent("X"), IndexComponent(1))
    >>> atom_c = Atom(NameComponent("C"), ResidueComponent("Y"), IndexComponent(2))
    >>> a_iter = AtomIterator([atom_a, atom_b, atom_c])
    >>> assert list(a_iter) == [(atom_a,), (atom_b,), (atom_c,)]

    Subclasses are iterators that can be passed between each other via functions inherited from
    this class. 'collect' flattens grouping back into a list of atoms.
    >>> a_iter = AtomIterator([atom_a, atom_b, atom_c])
    >>> a_list = a_iter.group_by("resname").filter("name", none_of=["B"]).collect()
    >>> assert a_list == [atom_c]

    Sort atoms based on a given key property.
    >>> a_iter = AtomIterator([atom_a, atom_b, atom_c])
    >>> a_list = a_iter.sort("index").group_by("resname").collect()
    >>> assert a_list == [atom_b, atom_c, atom_a]
    """

    def __init__(self, atoms: Iterable[Atom] = None):
        if atoms:
            self._atom_groups = iter(atoms)

    def __next__(self):
        return (next(self._atom_groups),)

    def __iter__(self):
        return self

    def group_by(self, key: str):
        return GroupIterator(self, key)

    def filter(self, key:str, any_of: None | Iterable = None, none_of: None | Iterable = None):
        return FilterIterator(self, key, any_of, none_of)

    def collect(self) -> list[Atom]:
        return [atm for grp in self for atm in grp]

    def sort(self, key: str):
        return AtomIterator(sorted(self.collect(), key=lambda a: a[key]))

    def write(self, path: str):
        pass

class GroupIterator(AtomIterator):

    """
    Dispenses sequential atoms grouped by a given aspect.

    >>> from atomflow.atom import Atom
    >>> from atomflow.components import NameComponent, ResidueComponent

    >>> atom_a = Atom(NameComponent("A"), ResidueComponent("X"))
    >>> atom_b = Atom(NameComponent("B"), ResidueComponent("Y"))
    >>> atom_c = Atom(NameComponent("B"), ResidueComponent("X"))
    >>> g_iter = GroupIterator([(atom_a, atom_b, atom_c)], group_by="name")
    >>> assert list(g_iter) == [(atom_a,), (atom_b, atom_c)]

    Only collects sequential similar atoms.
    >>> g_iter = GroupIterator([(atom_a, atom_b, atom_c)], group_by="resname")
    >>> assert list(g_iter) == [(atom_a,), (atom_b,), (atom_c,)]
    """

    def __init__(self, atom_groups, group_by):

        super().__init__()

        self._atom_groups = iter(atom_groups)
        self._group_by = group_by

        self._last_value = None
        self._queue = deque()
        self._source_state = None
        self._buffer = []

    def __next__(self):

        # If no atoms left to dispense, signal end of iteration
        if self._source_state == END:
            raise StopIteration

        while True:

            # If the queue is empty
            if len(self._queue) == 0:

                # Try to withdraw the next group of atoms from the source, and add to the queue
                try:
                    next_group = next(self._atom_groups)
                    self._queue.extend(next_group)

                # If source is empty, return the remaining buffer contents and set up end of iterator
                except StopIteration:
                    self._source_state = END
                    return tuple(self._buffer)

            # Get the next atom and its grouping value
            atom = self._queue.popleft()
            value = atom[self._group_by]

            # If the atom is the first, or it has the same grouping value as the previous, add it to the buffer
            if self._last_value in (None, value):
                self._buffer.append(atom)
                self._last_value = value

            # If the atom has a new grouping value, output the buffer and reinitialise with this atom
            else:
                out = self._buffer[:]
                self._buffer = [atom]
                self._last_value = value
                return tuple(out)


class FilterIterator(AtomIterator):

    """
    Filters Atoms based on either allowed or disallowed values of the given aspect (key).

    >>> from atomflow.atom import Atom

    >>> atom_a = Atom(NameComponent("A"))
    >>> atom_b = Atom(NameComponent("B"))
    >>> atom_groups = [(atom_a,), (atom_b,)]
    >>> f_iter = FilterIterator(atom_groups, "name", none_of=["B"])
    >>> assert list(f_iter) == [(atom_a,)]

    If any one atom in a group matches the any_of or none_of conditions, the whole group is included or
    excluded, respectively.

    >>> atom_c = Atom(NameComponent("C"))
    >>> atom_groups = [(atom_a, atom_c), (atom_b,)]
    >>> f_iter = FilterIterator(atom_groups, "name", none_of=["C"])
    >>> assert list(f_iter) == [(atom_b,)]

    >>> f_iter = FilterIterator(atom_groups, "name", any_of=["A"])
    >>> assert list(f_iter) == [(atom_a, atom_c)]
    """

    def __init__(self, atom_groups, key,
                 any_of: None | Iterable = None, none_of: None | Iterable = None):

        super().__init__()

        self._atom_groups = iter(atom_groups)
        self.key = key

        if any_of is None:
            self.filter = lambda group: not any(atom[key] in none_of for atom in group)
        elif none_of is None:
            self.filter = lambda group: any(atom[key] in any_of for atom in group)
        else:
            raise ValueError("One of 'any_of' or 'none_of' must be provided")

    def __next__(self):
        while True:
            group = next(self._atom_groups)
            if self.filter(group):
                return group


if __name__ == '__main__':
    pass