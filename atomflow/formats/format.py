from abc import ABC, abstractmethod
from collections.abc import Iterable
import os

from atomflow.atom import Atom

class Format(ABC):

    @classmethod
    @abstractmethod
    def read_file(cls, path: str | os.PathLike) -> list[Atom]:
        ...

    @classmethod
    @abstractmethod
    def to_file(cls, atoms: Iterable[Atom], path: str | os.PathLike) -> None:
        ...