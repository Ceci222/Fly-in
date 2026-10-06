class MapParser:
    def __init__(self, path: str) -> None:
        self.path = path


def parse() -> None:
    with open("maps/medium/01_dead_end_trap.txt", "r", encoding="utf-8") as file:
        lines: list[tuple[int, str]] = list(enumerate(file, start=1))

    for line_nbr, line_text in lines:
        print(line_nbr, line_text.rstrip("\n"))

