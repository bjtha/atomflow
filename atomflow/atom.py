class Atom:
    def __init__(self):
        self._by_aspect = {}

    def __getattr__(self, item):
        for fts in self._by_aspect.values():
            ft = fts[-1]
            if a := getattr(ft, item, None):
                return a
        raise AttributeError(f"No feature with '{item}' property.")

    def add(self, ft):
        for asp in ft.aspects:
            self._by_aspect.setdefault(asp, []).append(ft)

    def implements(self, aspect):
        return aspect in self._by_aspect
