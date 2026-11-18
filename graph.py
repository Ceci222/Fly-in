from models import Zone, Connection


class Graph:
    def __init__(self, zones: dict[str, Zone],
                 connections: list[Connection],
                 start_hub_name: str,
                 end_hub_name: str) -> None:
        # They'll be received as params, the rest are produced by class
        self.zones = zones
        self.start_hub = start_hub_name
        self.end_hub = end_hub_name
        self.connections = connections
        self.neighbors: dict[str, list[tuple[str, Connection]]] = {}

        for hub_name in zones:
            self.neighbors[hub_name] = []
        for connection_obj in connections:
            self.neighbors[connection_obj.path_a].append(
                (connection_obj.path_b, connection_obj))
            self.neighbors[connection_obj.path_b].append(
                (connection_obj.path_a, connection_obj))
