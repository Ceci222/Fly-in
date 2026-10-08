
from pydantic import BaseModel, Field, model_validator, ConfigDict
from enum import Enum


class ZoneType(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"
    PRIORITY = "priority"


class Zone(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str = Field(min_length=1)
    # By default, Pydantic will attempt to coerce values
    # to the desired type when possible.
    # ConfigDict(strict=True) receives the data from parser
    # and keeps it as is  or rejects it
    # Will be received as str from .txt and parsed to int,
    # that's what pydantic will validate
    coord_x: int
    coord_y: int
    # Despite having no field they are protected by strict=Tru,
    # no field 'cause admits any coordinate even negative
    color: str | None = None  # None by default
    max_drones: int | None = Field(default=1, gt=0)
    # max num of drone that can be in an area at the same time
    zone_type: ZoneType = ZoneType.NORMAL
    # I pass the class attribute as a value

    @model_validator(mode="after")
    def validate_input_name(self) -> "Zone":
        # pydantic requires full class to check it
        # and to return an object of that class
        # "zone" is a tentative name because by the time the
        #  hint is written the class itself is till being defined
        if "-" in self.name or " " in self.name:
            raise ValueError("Input name cannot contain '-' nor ' '.")
        return self  # the validated instance must be returned


class Connection(BaseModel):
    model_config = ConfigDict(strict=True)
    path_a: str = Field(min_length=1)
    path_b: str = Field(min_length=1)
    max_link_capacity: int = Field(default=1, gt=0)
    # nbr of drones crossing at the same time


class MapParser:
    def __init__(self, path: str) -> None:
        self.path = path  # comes from the map, the rest have already been set
        self.nb_drones: int = 0
        self.zones: dict = {}
        self.connections: list = []

    def parse(self) -> None:
        nb_drone_data_counter = 0
        with open(self.path, "r",
                  encoding="utf-8") as file:
            lines: list[tuple[int, str]] = list(enumerate(file, start=1))

        for line_nbr, line_text in lines:
            print(line_nbr, line_text.rstrip("\n"))

        for line_nbr, line_text in lines:
            line = line_text.strip()
            if line == "":  # Removes spaces, if get empty line continue
                # if line == "" is the same as if not line
                # -> if line has no content
                continue
            if line.startswith("#"):
                continue
            elif line.startswith("nb_drones:"):
                self.nb_drones = line.removeprefix("nb_drones:")
                if self.nb_drones == "":
                    raise ValueError(
                        f"line {line_nbr}: nb_drones has no value")
                else:
                    self.nb_drones = int(self.nb_drones.lstrip())
                    nb_drone_data_counter += 1
                    if nb_drone_data_counter > 1:
                        raise ValueError(
                            f"line {line_nbr}: nb_drones has already been "
                            f"declared")
                    if self.nb_drones <= 0:
                        raise ValueError(
                            f"line {line_nbr}: nb_drones must be a positive "
                            f"value")
            # line_nbr es sólo variable de iteración, el "ínidice" que crea
            # solo es temporal dentro del for no se accede desde fuera
                    print(f"Nb or drones: {self.nb_drones}")

def main()-> None:
    map = MapParser("maps/medium/01_dead_end_trap.txt")
    map.parse()

if __name__== "__main__":
    main()