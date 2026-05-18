"""Run the target tiller program"""

import sys

from .cli import CLI


def main() -> None:
    """Create an instance of CLI (with the command line arguments) and run it."""
    CLI(sys.argv[1:]).run()

if __name__ == "__main__":
    main()
