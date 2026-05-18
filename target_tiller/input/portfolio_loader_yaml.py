"""This module defines the PortfolioLoaderYAML class"""

import yaml

from ..portfolio import Portfolio


class PortfolioLoaderYAML:
    """This class loads a portfolio defined by a YAML format."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self._portfolio = None
        self._raw = None
        self._cash = None
        self._name = None

    @property
    def raw(self) -> dict:
        """The parsed parts of the file (loading as needed)."""
        if not self._raw:
            with open(self.filename, encoding="utf-8") as file:
                raw = yaml.load(file, Loader=yaml.SafeLoader)
                if list(raw.keys()) == ["portfolio"]:
                    self._raw = raw["portfolio"]
                else:
                    self._raw = raw

        return self._raw

    @property
    def name(self) -> str:
        """The name of the portfolio."""
        if self._name is None:
            if self.raw.get("name"):
                self._name = self.raw["name"]
            else:
                self._name = ""

        return self._name

    @property
    def cash(self) -> float:
        """The cash held by the portfolio."""
        if self._cash is None:
            if self.raw.get("cash"):
                self._cash = self.raw["cash"]
            else:
                self._cash = 0.0

        return self._cash

    @property
    def portfolio(self) -> Portfolio:
        """The Portfolio object created by loading the file."""
        if self._portfolio is None:
            holdings = {}
            if self.raw.get("holdings"):
                for holding in self.raw["holdings"]:
                    holdings[holding["symbol"]] = holding["amount"]
            self._portfolio = Portfolio(holdings, cash=self.cash, name=self.name)

        return self._portfolio
