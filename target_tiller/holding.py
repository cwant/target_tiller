"""This module defines the Holding class"""

class Holding:
    """This holds an amount (dollar value) of a specific security."""

    # TODO: maybe get rid of this class, it's kind of useless
    def __init__(self, symbol: str, value: float) -> None:
        self.symbol = symbol
        self.value = value
