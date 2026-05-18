"""Definition of the TransactionsConfig class."""

from typing import TYPE_CHECKING

from .balancers import BuyOnlyBalancer, BuySellBalancer, SellOnlyBalancer

if TYPE_CHECKING:
    from .balancers import Balancer


class TransactionsConfig:
    """Configuration for the transactions that should be done to an account."""

    DEFAULT_MINIMUM_TRANSACTION = 100
    DEFAULT_MAXIMUM_TRANSACTION = 10000

    def __init__(self, **transactions_config_hash: str) -> None:
        """transactions_config hash has metadata about portfolio, balancer info,
        and amount of inflow/outflow.

        E.g.,
        { 'portfolio_name': 'ABC123',
          'nickname': 'My nest egg',
          'action': 'buy_only',
          'amount': 5000.0 }
        """
        self._config = transactions_config_hash
        self._balancer_class = None

        self.validate()

    def validate(self) -> None:
        """Test that an TransactionsConfig object is valid."""
        if self.balancer_class is None:
            raise ValueError(f"{self.action} is not a valid action")

        if self.amount <= 0 and self.action == "buy_only":
            raise ValueError("Must have positive flow if only buying")
        if self.amount >= 0 and self.action == "sell_only":
            raise ValueError("Must have negative flow if only selling")

    @property
    def portfolio_name(self) -> str:
        """Return the name of the portfolio."""
        return self._config.get("portfolio_name")

    @property
    def nickname(self) -> str:
        """Return the nickname for the portfolio."""
        return self._config.get("nickname")

    @property
    def action(self) -> str:
        """Return the action to be performed on the portfolio."""
        return self._config.get("action")

    @property
    def amount(self) -> float:
        """Return the amount of the transaction to be performed on the portfolio."""
        return self._config.get("amount", 0)

    @property
    def minimum_transaction(self) -> float:
        """Return the least amount of money changing for either spend/withdrawal
        during a transaction.
        """
        return self._config.get("minimum_transaction",
                                 self.DEFAULT_MINIMUM_TRANSACTION)

    @property
    def maximum_transaction(self) -> float:
        """Return the greatest amount of money changing for either spend/withdrawal
        during a transaction.
        """
        return self._config.get("maximum_transaction",
                                 self.DEFAULT_MAXIMUM_TRANSACTION)

    @property
    def balancer_class(self) -> "Balancer":
        """Return the balancer class to be used on the portfolio."""
        balancer_class_map = {
            "buy_only": BuyOnlyBalancer,
            "buy_sell": BuySellBalancer,
            "sell_only": SellOnlyBalancer
        }

        if not self._balancer_class:
            self._balancer_class = balancer_class_map.get(self.action)
        return self._balancer_class

    def dump(self) -> dict:
        """Return a hash representing this object."""
        return self._config

    # Meh, I don't like that I'm only defining these to make tests easier
    def __eq__(self, other: "TransactionsConfig") -> bool:
        if isinstance(other, TransactionsConfig):
            return \
                [self.portfolio_name, self.nickname,
                 self.action, self.amount,
                 self.minimum_transaction, self.maximum_transaction] == \
                 [other.portfolio_name, other.nickname,
                  other.action, other.amount,
                  other.minimum_transaction, other.maximum_transaction]
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.portfolio_name, self.nickname,
                    self.action, self.amount,
                    self.minimum_transaction, self.maximum_transaction)

    def __repr__(self) -> str:
        return f"TransactionsConfig('{self.portfolio_name}', '{self.nickname}', "\
            "'{self.action}', {self.amount}, "\
            "{self.minimum_transaction}, {self.maximum_transacion})"
