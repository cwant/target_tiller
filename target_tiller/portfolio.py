"""This module defines the Portfolio class"""

import math
from typing import TYPE_CHECKING

from .holding import Holding
from .transaction import Transaction

if TYPE_CHECKING:
    from .targets import Targets


class Portfolio:
    """This holds a bunch of securities and their dollar values for
    an account. Also holds cash.
    """

    SMALL_CHANGE = 0.01

    def __init__(self, holdings: dict | list,
                 cash: float | None = None,
                 name: str | None = None) -> None:
        """Initializes the Portfolio object based on a hash of
        security (symbols) and associated values.
        E.g.,
        { "IBM": 9845.39,
          "SGI": 134.56 }
        """
        self._holdings = {}
        if isinstance(holdings, dict):
            for symbol in holdings:
                value = holdings[symbol]
                self._holdings[symbol] = Holding(symbol, value)
        else:
            for holding in holdings:
                self._holdings[holding.symbol] = holding

        self._holdings_value = None
        self._weights = None
        self._symbols = None
        self._cash = cash
        self._name = name

    def dump_holdings(self) -> dict:
        """Return a dictionary of securities and values"""
        out = {}
        for symbol, holding in self._holdings.items():
            out[symbol] = holding.value
        return out

    def dump(self) -> dict:
        """Return a hash representing this object."""
        out = {"holdings": self.dump_holdings(),
               "cash": self.cash}
        if self.name:
            out["name"] = self.name

        return out

    def merge(self, other: "Portfolio") -> "Portfolio":
        """Merge two Portfolios, return a new Portfolio object.
        Overwrite holding from other Portfolio with holdings in
        this Portfolio object. Do not copy cash or name from other.
        """
        holdings = other.holdings.copy()

        for symbol in self.symbols:
            holdings[symbol] = self.holding(symbol)
        output = Portfolio(holdings.values(), cash=self._cash, name=self._name)
        return output

    def include_empty_targets(self, targets: "Targets") -> None:
        """Set values of 0.0 for any symbols in targets that
        don't exist in this Portfolio object
        """
        for symbol in targets.symbols:
            if symbol not in self._holdings:
                self._holdings[symbol] = Holding(symbol, 0.0)

    def targeted_value(self, targets: "Targets" = None) -> float:
        """What is the current value of only the holdings we are targeting?"""
        if not targets:
            return None

        out = 0
        for symbol in sorted(set(list(self.symbols) + list(targets.symbols))):
            if symbol in targets.symbols:
                out += self.holding(symbol).value

        return out

    def targeted_proportion(self, targets: "Targets" = None) -> float:
        """The proportion of the portfolio that is taken up by securities
        represented by the targets argument.
        """
        if not targets:
            return None

        if self.holdings_value == 0:
            return 0

        return self.targeted_value(targets) / self.holdings_value

    def targeted_proportion_including_cash(self, targets: "Targets" = None) -> float:
        """The proportion of the portfolio that is taken up by securities
        represented by the targets argument, including cash.
        """
        if not targets:
            return None

        return self.targeted_value(targets) / self.total_value

    def diff(self, other: "Portfolio") -> dict:
        """Returns a hash that provides the difference in value for each
        security between this Holding and the other one.
        E.g., if this one has 500 of "SGI" and the other has 250 or "SGI",
        then the diff is {"SGI": 250}.
        """
        out = {}
        for symbol in self.symbols:
            out[symbol] = self.holding(symbol).value - other.holding(symbol).value
        return out

    def transactions(self, other: "Portfolio", targets: "Targets" = None) -> list:
        """What transactions would needed to turn the other Holdings
        into this one. E.g., if this one has 400 "SGI" and the other has 250,
        and if this one has 100 "IBM" and the other has 200, then the
        output is [["SGI", "Buy", 150], ["IBM", "Hold", None]].
        As seen above, it the other has more of a security than this one,
        then don't buy anymore (future extension: sell)
        """
        diff = self.diff(other)

        out = []
        for symbol in sorted(diff):
            if targets and symbol not in targets.symbols:
                continue
            change = diff[symbol]
            if change > self.SMALL_CHANGE:
                out.append(Transaction(symbol, "Buy", change))
            elif change < -self.SMALL_CHANGE:
                out.append(Transaction(symbol, "Sell", -change))
            else:
                out.append(Transaction(symbol, "Hold", None))
        return out

    def actual_change(self, other: "Portfolio") -> float:
        """How much is spent/withdrawn when turning the other portfolio's holdings
        into this one
        """
        return self.holdings_value - other.holdings_value

    def target_distance(self, targets: "Targets") -> float:
        """A measure of how far from our targets we are.
        0.0 means we completely match the target proportions.
        """
        total = 0
        holdings = targets.filter_portfolio(self)
        for symbol in targets.symbols:
            total += (holdings.weight(symbol) - targets.weight(symbol))**2
        return math.sqrt(total)

    def balance(self, targets: "Targets") -> float:
        """1.0 means we completely match the target proportions."""
        return 1.0 - self.target_distance(targets)

    @property
    def symbols(self) -> list:
        """Return the symbols of the securities we hold"""
        if not self._symbols:
            self._symbols = self._holdings.keys()
        return self._symbols

    @property
    def holdings_value(self) -> float:
        """The value of just the security holdings (not including cash)"""
        if not self._holdings_value:
            self._holdings_value = 0
            for symbol in self._holdings:
                self._holdings_value += self.holding(symbol).value
        return self._holdings_value

    @property
    def cash(self) -> float:
        """The amount of cash held by the holdings."""
        return self._cash

    @cash.setter
    def cash(self, value: float) -> None:
        """Set the amount of cash held by the holdings."""
        self._cash = value

    @property
    def name(self) -> str:
        """The amount of cash held by the holdings."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name."""
        self._name = value

    @property
    def total_value(self) -> float:
        """The value of the portfolio, including cash."""
        return self.holdings_value + self.cash

    @property
    def holdings(self) -> list:
        """The holdings of the portfolio"""
        return self._holdings

    def holding(self, symbol: str) -> Holding:
        """Return the holding for a specific security (by symbol)."""
        if symbol not in self._holdings:
            return 0

        return self._holdings[symbol]

    def weight(self, symbol: str) -> float:
        """The proportion of a security compared to the value of all
        securities (by symbol). Not including cash.
        """
        if symbol not in self._holdings:
            return 0

        if self.holdings_value == 0:
            return 0

        if not self._weights:
            self._weights = { s: (holding.value / self.holdings_value)
                              for s, holding in self.holdings.items() }
        return self._weights[symbol]
