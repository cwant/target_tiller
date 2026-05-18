"""This module defines the Targets class"""

from .portfolio import Portfolio


class Targets:
    """This contains the weights we wish some securities had
    for a portfolio (e.g., 0.20 or 20% in bonds).
    """

    def __init__(self, targets_hash: dict) -> None:
        """targets_hash has weights indexed by symbol in a dictionary.
        E.g.,
        { "IBM": 0.4,
          "SGI": 0.6 }
        """
        self._targets = targets_hash

    def weight(self, symbol: str) -> float:
        """The proportion desired of a symbol within a portfolio."""
        return self._targets[symbol]

    def dump(self) -> dict:
        """Return a dict representing this object."""
        return self._targets

    @property
    def symbols(self) -> list:
        """Return the symbols for the all the securities we know about"""
        return self._targets.keys()

    def filter_portfolio(self, portfolio: Portfolio) -> Portfolio:
        """Create a new Portfolio object (from the supplied portfolio argument)
        for only the symbols we know about.
        """
        out_portfolio = {}
        for s in self.symbols:
            holding = portfolio.holding(s).value \
                if (s in portfolio.symbols) else 0
            out_portfolio[s] = holding

        return Portfolio(out_portfolio)
