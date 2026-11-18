from graph import Graph
from models import ZoneType
import heapq


class Pathfinder:
    """Find the paths the drones will use to go from start to end.

    Aim:
        Search the graph for paths from the start zone to the end zone
        and give them back sorted from cheapest to most expensive.

    Usage:
        It receives the graph already built (zones, neighbors, start and
        end) and works only with zone names: a path is a list of zone
        names in order, from the start zone to the end zone,
        e.g. ["start", "junction", "goal"].
    """
    def __init__(self, graph: Graph):
        """Store the graph of the current map.

        Aim:
            Keep the graph so every method can reach the zones dictionary
            (self.graph.zones) and the neighbors of each zone
            (self.graph.neighbors).

        Args:
            graph: the Graph object of the current map.

        Usage:
            main.py creates the Graph after parsing the map and passes it
            here when it creates the Pathfinder.
        """
        self.graph = graph
        self.zones = graph.zones
        self.start_hub_name = graph.start_hub
        self.end_hub_name = graph.end_hub

    def calculate_turn_cost(self, zone_name: str) -> int:
        """Return how many turns a drone needs to enter this zone.

        Aim:
            self.graph.zones is a dictionary: the key is the zone name as
            written in the map (e.g. "junction") and the value is its Zone
            object. With the name we get the Zone, and from the Zone we
            read its zone_type attribute (one of the ZoneType enum
            members), which we compare with RESTRICTED.

        Args:
            zone_name: name of the zone to check.

        Returns:
            2 if the zone is RESTRICTED (the drone spends one turn flying
            over the connection and lands the next one), 1 otherwise.

        Usage:
            zone_name is filled in by the method that calls this one
            (calculate_path_costs, find_shortest_path). BLOCKED zones never get
            here: they are skipped before.
        """
        if self.graph.zones[zone_name].zone_type == ZoneType.RESTRICTED:
            return (2)
        return (1)

    def calculate_priority_cost(self, zone_name: str) -> int:
        """Return the tie-break cost of entering this zone.

        Aim:
            Priority zones must be preferred. This is a second cost, not
            turns: it only decides between paths that take the same number
            of turns. Lower is better, so a PRIORITY zone costs 0 and any
            other zone costs 1.

        Args:
            zone_name: name of the zone to check, used as the key of
                self.graph.zones (same as in calculate_turn_cost).

        Returns:
            0 if the zone is PRIORITY, 1 otherwise.

        Usage:
            zone_name is filled in by the method that calls this one
            (calculate_path_costs, find_shortest_path).
        """
        if self.graph.zones[zone_name].zone_type == ZoneType.PRIORITY:
            return (0)
        return (1)

    def calculate_path_costs(self, path: list[str]) -> tuple[int, int]:
        """Return real cost of a finished path in terms of turns & priority.

        Aim:
            It only measures the path it receives; it does not search.
            Calculates the costs in terms of priority and turns of each path
            based on the total addition of the turns and non_priority zones of
            each path.

        Args:
            path: list of zone names in order, from start to end,
                e.g. ["start", "junction", "goal"].

        Returns:
            One tuple (turns, priority cost). Two tuples are compared
            first by turns; only if turns are equal, by priority cost.
            The smaller one wins: (2, 1) beats (2, 2), and (2, 2)
            beats (3, 0).

        Usage:
            The path is built by find_shortest_path.
            This method (calculate_path_costs) is required by find_paths which
            calls it with each path to sort them from cheapest to most
            expensive.

            This real cost is needed because the cost find_shortest_path adds while
            searching includes an extra penalty for zones already used (in
            find_paths the usage variable keeps track of used zones).

            The first zone (path[0]) is the start zone: the drone is already
            there, so entering it costs nothing. That is why the loop goes
            through path[1:], from the second zone to the end.
        """
        turns_cost = 0
        priority_cost = 0

        for zone_name in path[1:]:
            turns_cost += self.calculate_turn_cost(zone_name)
            priority_cost += self.calculate_priority_cost(zone_name)

        return (turns_cost, priority_cost)

    def find_shortest_path(self, zn_usage: dict[str, int]) -> list[str] | None:
        """Return the cheapest path from start to end, or None if none.

        Aim:
            Dijkstra's algorithm. It explores the graph from the start
            zone, always going on from the pending zone that has been
            reached most cheaply so far. The first time the end zone comes
            out of the queue, it has been reached by the cheapest path.

            It uses three working variables:
            - known_zn_n_costs: zone name -> (turns, priority cost) to reach
              that zone from the start. A zone is saved the first time it
              is found as a neighbor. Both values are sums from the start:
              turns adds calculate_turn_cost (plus the zn_usage penalty)
              and priority cost adds calculate_priority_cost. The start
              zone is (0, 0).
            - previous_zn: zone name -> the zone it was reached from
              (e.g. previous_zn["junction"] = "start"). At the end it is
              used to rebuild the path backwards, from the end zone to the
              start, and then the path is reversed.
            - pending_zn_queue: zones still to explore, as tuples
              (turns, priority cost, zone name). heapq.heappop always takes
              out the smallest tuple. It is a list of tuples and not of
              dictionaries because heapq has to compare its elements, and
              dictionaries cannot be compared with <. The costs go first
              and the name last because tuples are compared from the first
              element: fewest turns first, then lowest priority cost, and
              the name only breaks a full tie. With the name first, zones
              would come out in alphabetical order, not by cost.

            Each loop: take the cheapest pending zone. If it is the end
            zone, rebuild the path and return it. Otherwise, look at each
            of its neighbors: skip it if it is BLOCKED or already in
            known_zn_n_costs; if not, compute the cost of reaching it through
            this zone, save it in known_zn_n_costs and previous_zn and push it
            into the queue.

            A neighbor already in known_zn_n_costs is never checked again for
            a cheaper cost: the cost of entering a zone depends only on
            that zone (its type and its zn_usage penalty), not on where the
            drone comes from, and the queue gives zones out from cheapest
            to most expensive, so the first cost saved is always the best.

        Args:
            zn_usage: zone name -> how many times the paths already found
                use that zone (e.g. {"junction": 2}). Each use adds one
                turn to the cost of entering the zone, so the search tends
                to avoid zones already used. Empty ({}) the first time.

        Returns:
            The path as a list of zone names in order, from start to end,
            e.g. ["start", "junction", "goal"]. None if the end zone
            cannot be reached (e.g. BLOCKED zones cut every path).

        Usage:
            find_paths calls it several times and adds to zn_usage after
            each path, so that alternative paths come out. It does not
            check whether the path is new: find_paths discards repeated
            ones. The cost it uses inside includes the zn_usage penalty,
            so the real cost of a path is computed afterwards by
            calculate_path_costs.
        """
        known_zn_n_costs: dict[str, tuple[int, int]] = {
            self.start_hub_name: (0, 0)
        }

        previous_zn: dict[str, str] = {}  # find prev zn of key
        pending_zn_queue: list[tuple[int, int, str]] = [(0, 0, self.start_hub_name)]

        while pending_zn_queue:
            turns_so_far, priority_so_far, zone = heapq.heappop(pending_zn_queue)
            if zone == self.end_hub_name:
                path: list[str] = []
                path.append(self.end_hub_name)
                while zone in previous_zn:
                    zone = previous_zn[zone]
                    path.append(zone)
                return path[::-1]
            
            for neighbor, _ in self.graph.neighbors[zone]:
                if self.zones[neighbor].zone_type == ZoneType.BLOCKED:
                    continue  # next neighbor 'cause it's iterating the list of neighbors
                if neighbor in known_zn_n_costs:  # for previous neighbors already in the dict
                    continue
            
                neighbor_turn_cost = self.calculate_turn_cost(neighbor)  # how much it'd cost to enter
                neighbor_priority_cost = self.calculate_priority_cost(neighbor)

                if neighbor in zn_usage:
                    penalty = zn_usage[neighbor]
                else:
                    penalty = 0

                turns_till_neighbor =  turns_so_far + neighbor_turn_cost + penalty  #the toal up to there
                priority_till_neighbor = priority_so_far + neighbor_priority_cost 

                known_zn_n_costs[neighbor] = (turns_till_neighbor, priority_till_neighbor)
                previous_zn[neighbor] = zone  # previous zn of the neighbor

                heapq.heappush(pending_zn_queue, (turns_till_neighbor, priority_till_neighbor, neighbor))

        return None
 

            



