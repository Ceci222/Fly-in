from pydantic import (BaseModel, Field, model_validator, ConfigDict)
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
    GRAY = "gray"


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
    max_drones: int | None
    # max num of drone that can be in several areas at the same time
    zone_type: ZoneType = ZoneType.NORMAL
    # I pass the class attribute as a value

    # This is an intermediate step between passing a value for the color
    # attribute and assigning it to the object
    # It checks that the given value is within the enum accepted values.
    # If it is, it assigns the value to the attribute, else it raises an error
    # Returns something like Colors.GREEN and that's what's assigned to the
    # attribute
    @model_validator(mode="after")  # receives the converted and validated
    # object, then applies rules to it
    def validate_input_name(self) -> "Zone":
        # pydantic requires full class to check it
        # and to return an object of that class
        # "zone" is a tentative name because by the time the
        #  hint is written the class itself is till being defined
        if "-" in self.name or " " in self.name:
            raise ValueError("Input name cannot contain '-' nor ' '.")
        return self  # the validated instance must be returned

# The decorator decides when the function runs, either before the type
# validation or after
# The instatiation is not over until the validation is complete
# mode="after" is for after Pydandic's done validating fields, data types,
# etc... It either insatiates or doesn't
# mode="before" is for "corrections". If there is something wrong I get to
# think of an alternative before the data type is
# validated by pydantic. I either have what the enum allows, or I may
# provide an alternative value, for example.
# It is a classmethod because the object doesn't exist yet, so it can't
# receive self


"""
    @field_validator("color", mode="before")  # "color" the name of the
    # field to be validated
    @classmethod  # There is no object yet, so no self can be received as
    # an arg, just cls
    def validate_color(cls, color: Colors | None = None) -> Colors | None:
        # it doesn't admit a string but an object from the enum
        if color is None:
            return None
        try:
            return Colors(color)  # if the color exists within the the enum
            # it is returned, else the except takes over
        except ValueError:
            print("Since no valid color has been provided, none will be used")
            return None"""


# model validator receives the whole object, field validator receives the
# field instead
# it receives two params, the field on which it's applied and the
# execution mode
# positional args should go before keyargs (syntax -> mode='after')
class Connection(BaseModel):
    model_config = ConfigDict(strict=True)  # pydantic stric, not automatic
    # data casting
    path_a: str = Field(min_length=1)
    path_b: str = Field(min_length=1)
    max_link_capacity: int = Field(default=1, gt=0)
    # nbr of drones crossing at the same time
