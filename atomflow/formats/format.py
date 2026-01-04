from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
import os

from atomflow.atom import Atom


class Format(ABC):

    _register = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for ext in cls.extensions:
            Format._register[ext] = cls

    @classmethod
    def get_format(cls, ext: str) -> Format:
        try:
            return cls._register[ext]
        except KeyError:
            raise ValueError(f"No format found for extension '{ext}'")

    @property
    @abstractmethod
    def extensions(self) -> tuple[str]:
        ...

    @property
    @abstractmethod
    def recipe(self) -> Mapping:
        ...

    @classmethod
    @abstractmethod
    def read_file(cls, path: str | os.PathLike) -> list[Atom]:
        ...

    @classmethod
    @abstractmethod
    def to_file(cls, atoms: Iterable[Atom], path: str | os.PathLike) -> None:
        ...