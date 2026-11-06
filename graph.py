from models import Zone, Connection


class Graph:
    def __init__(self, zones: dict[str, Zone],
                 connections: list[Connection]) -> None:
        self.zones = zones
        self.connections = connections
        self.neighbors: dict[str, list[tuple[str, Connection]]] = {}
        for hub_name in zones:
            self.neighbors[hub_name] = []
        for connection_obj in connections:
            self.neighbors[connection_obj.path_a].append(
                (connection_obj.path_b, connection_obj))
            self.neighbors[connection_obj.path_b].append(
                (connection_obj.path_a, connection_obj))
