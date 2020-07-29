
class Controller:

    def __init__(self, name, base_ref, runways_map):
        self._name = name
        self._base_ref = base_ref
        self._registry = []
        self._runways_map = runways_map

    def _add_flight(self, plane):
        self._registry.append(plane)
        return


class TowerController(Controller):
    def _a(self):
        return


class GroundController(Controller):
    def _a(self):
        return

