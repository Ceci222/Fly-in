from parser import MapParser
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)
    try:
        map = MapParser(sys.argv[1])
        """
        python3 main.py maps/easy/02_simple_fork.txt
        sys.argv = ["main.py", "maps/easy/02_simple_fork.txt"]
                      [0]                [1]
        """
        map.parse()
    except ValueError as e:
        print(f"{e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Program has been interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
