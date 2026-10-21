
from pydantic import BaseModel, Field, model_validator, ConfigDict, field_validator
from enum import Enum


class ZoneType(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"
    PRIORITY = "priority"

class Colors(Enum):
    BLACK = "black"
    BLUE = "blue"
    BROWN = "brown"
    CRIMSON = "crimson"
    CYAN = "cyan"
    DARKRED = "darkred"
    GOLD = "gold"
    GREEN = "green"
    LIME = "lime"
    MAGENTA = "magenta"
    MAROON = "maroon"
    ORANGE = "orange"
    PURPLE = "purple"
    RAINBOW = "rainbow"
    RED = "red"
    VIOLET = "violet"
    YELLOW = "yellow"

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
    color: Colors | None = None  # None by default
    max_drones: int | None = Field(default=1, gt=0)
    # max num of drone that can be in an area at the same time
    zone_type: ZoneType = ZoneType.NORMAL
    # I pass the class attribute as a value

    # This is an intermediate step between passing a value for the color attribute and assigning it to the object
    # It checks that the given value is within the enum accepted values. 
    # If it is, it assigns the value to the attribute, else it raises an error
    # Returns something like Colors.GREEN and that's what's assigned to the attribute
    @model_validator(mode="after") # receives the converted and validated object, then applies rules to it
    def validate_input_name(self) -> "Zone":
        # pydantic requires full class to check it
        # and to return an object of that class
        # "zone" is a tentative name because by the time the
        #  hint is written the class itself is till being defined
        if "-" in self.name or " " in self.name:
            raise ValueError("Input name cannot contain '-' nor ' '.")
        return self  # the validated instance must be returned

# The decorator decides when the function runs, either before the type validation or after
# The instatiation is not over until the validation is complete
# mode="after" is for after Pydandic's done validating fields, data types, etc... It either insatiates or doesn't
# mode="before" is for "corrections". If there is something wrong I get to think of an alternative before the data type is
# validated by pydantic. I either have what the enum allows, or I may provide an alternative value, for example.
# It is a classmethod because the object doesn't exist yet, so it can't receive self 
    @field_validator("color", mode="before")  # "color" the name of the field to be validated
    @classmethod  # There is no object yet, so no self can be received as an arg, just cls
    def validate_color(cls,color: Colors | None = None) -> "Zone": # it doesn't admit a string but an object from the enum
            if color is None:
                return None
            try:
                return Colors(color) # if the color exists within the the enum it is returned, else the except takes over
            except ValueError:
                print(f"{color} must be a valid color, default color will be used")
                return None
        
# model validator receives the whole object, field validator receives the field instead
# it receives two params, the field on which it's applied and the execution mode
# positional args should go before keyargs (syntax -> mode='after')
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
        start_hub_counter = 0
        end_hub_counter = 0

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
            # line_nbr is just and iteration avriable, the created "index"
            # is just temporary within the for loop. It cannot be accessed form outside the loop
                    print(f"Nb or drones: {self.nb_drones}")
            elif line.startswith("start_hub") or line.startswith("end_hub") or line.startswith("hub"):
                current_color = None
                current_max_drones = 1
                current_zone = ZoneType.NORMAL
                if line.startswith("start_hub"):
                    no_prefix_line = line.removeprefix("start_hub:")
                    start_hub_counter +=1
                    if start_hub_counter > 1:
                        raise ValueError(f"Line {line_nbr}: start_hub seems to appear more than once in the map")
                if line.startswith("end_hub"):
                    no_prefix_line = line.removeprefix("end_hub:")
                    end_hub_counter += 1
                    if end_hub_counter > 1:
                        raise ValueError(f"Line {line_nbr}: end_hub seems to appear more than once in the map")
                if line.startswith("hub"):
                    no_prefix_line = line.removeprefix("hub:")
                given_zone = no_prefix_line.split("[")  # returns a list of 2 elements, whatever was pre and post "["
                coord_and_name = given_zone[0].split()
                name, x, y = coord_and_name
                if len(given_zone) == 2:
                    metadata = given_zone[1].rstrip("]") #gotta remove the remaining bracket
                    splitted_metadata = metadata.split()
                    if len(splitted_metadata) >= 1 and len(splitted_metadata) <= 3:
                        for data in splitted_metadata:
                            parts = data.split("=")
                            if len(parts) != 2:
                                raise ValueError(f"Line {line_nbr}: Metadata requires 'key=value' format")
                            key, value = parts  # destructres for every turn, every data in the loop
                            if "color" == key:
                                current_color = value # Must have been set to none inictially so it doesn't break when insatantiated
                                # Can't be Colors(value) because this is castin not instantiation so it would try to turn to Enum something that's not on the list
                            elif "zone" == key:
                                current_zone = ZoneType(value)
                            elif "max_drones" == key:
                                current_max_drones = int(value)  # because with model_config = ConfigDict(strict=True) pydantic no loger casts by default
                            else:
                                raise ValueError(f"line {line_nbr}: The allowed metadata includes 'color', 'zone', 'max_drones'")
                elif len(given_zone) > 2:
                    raise ValueError(f"line {line_nbr}: a zone needs a name and two coordinates and optional metadata")

                map_zone = Zone(name = name, coord_x = int(x), coord_y = int(y), color = current_color, max_drones = current_max_drones, zone_type = current_zone)                    
                if name in self.zones:
                    raise ValueError(f"Line {line_nbr}: zone name '{name}' is duplicated")
                self.zones[name] = map_zone  # since self.zones is a dict I assign the zone to the key(the key is whatever I seva in "name")
        
        if nb_drone_data_counter == 0:
            raise ValueError("nb_drones is missing")
        if start_hub_counter == 0:
            raise ValueError("start_hub is missing")
        if end_hub_counter == 0:
            raise ValueError("end_hub is missing")
        
def main()-> None:
    map = MapParser("maps/medium/01_dead_end_trap.txt")
    map.parse()

if __name__== "__main__":
    main()