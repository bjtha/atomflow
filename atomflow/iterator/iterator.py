from collections import deque

from atomflow.atom import Atom
from atomflow.components import NameComponent, ResidueComponent

END = object()

class GroupIterator:

    def __init__(self, atom_groups, group_by):
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

    def __iter__(self):
        return self


def demo_group_iterator():
    atom_a = Atom(NameComponent("A"), ResidueComponent("X"))
    atom_b = Atom(NameComponent("B"), ResidueComponent("Y"))
    atom_c = Atom(NameComponent("C"), ResidueComponent("Y"))

    atoms = [(atom_a, atom_b, atom_c)]

    g_iter = GroupIterator(atoms, group_by="resname")
    for a in g_iter:
        print(a)
