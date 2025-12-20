from abc import abstractmethod

from atomflow.core import Aspect, Feature, Derivable

class HasName(Aspect):

    @property
    @abstractmethod
    def name(self) -> str: pass

    @classmethod
    def derive_from(cls, atom):
        if atom.implements(HasElement):
            return DerivedName(atom.element)


class NameFeature(Feature):

    aspects = (HasName,)

    def __init__(self, name):
        self._name = str(name)

    @property
    def name(self):
        return self._name


class DerivedName(Feature):

    aspects = (HasName,)

    def __init__(self, name):
        self._name = str(name)

    @property
    def name(self):
        return self._name


class HasElement(Aspect, Derivable):

    @property
    @abstractmethod
    def element(self) -> str: pass

    def derive(self, atom):
        if atom.implements(HasName):
            return DerivedElement(atom.name)

class ElementFeature(Feature):

    aspects = (HasElement,)

    def __init__(self, elem):
        self._elem = str(elem)

    @property
    def element(self):
        return self._elem


class DerivedElement(Feature):

    aspects = (HasElement,)

    def __init__(self, elem):
        self._elem = str(elem)

    @property
    def element(self):
        return self._elem