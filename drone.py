class Drone:
    def __init__(self, drone_id: int, path: list[str]) -> None:
        self.drone_id = drone_id
        self.path = path
        self.path_index = 0
        self.on_restricted_link = False

    def find_current_zone(self) -> str:
        zn_index = self.path_index
        current_zn_name = self.path[zn_index]
        return current_zn_name
    
    def find_next_zone(self) -> str:
        zn_index = self.path_index
        next_zn_name = self.path[zn_index + 1]
        return next_zn_name

    def count_zone_left(self) -> int:
        total_zn = len(self.path)
        zones_left = total_zn - (self.path_index + 1)
        return zones_left
    
    def move_to_next_zone(self) -> None:
        self.path_index = self.path_index + 1

    def land_on_restricted_zone(self)-> None:
        self.path_index = self.path_index + 1
        self.on_restricted_link = False
    
    def has_arrived(self) -> bool:
        if self.find_current_zone() == self.path[-1]:
            return True
        return False
    
    def move_to_restricted_link(self) -> None:
        self.on_restricted_link = True