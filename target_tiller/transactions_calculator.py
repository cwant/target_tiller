"""This module defines the TransactionsCalculator class"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .portfolio import Portfolio
    from .targets import Targets
    from .transactions_config import TransactionsConfig


class TransactionsCalculator:
    """This manages the pipeline for rebalancing a portfolio."""

    def __init__(self, portfolio: "Portfolio",
                 targets: "Targets",
                 transactions_config: "TransactionsConfig") -> None:
        self.initial_portfolio = portfolio
        self.final_portfolio = None

        self.targets = targets
        self.transactions_config = transactions_config

        self.balancer = None
        self.transactions = None

    def run(self) -> "TransactionsCalculator":
        """Perform the rebalancing described by the object."""
        balancer_class = self.transactions_config.balancer_class
        self.balancer = \
            balancer_class(portfolio=self.initial_portfolio,
                           targets=self.targets,
                           transactions_config=self.transactions_config)
        self.final_portfolio = \
            self.balancer.run().merge(self.initial_portfolio)
        self.transactions = \
            self.final_portfolio.transactions(self.initial_portfolio,
                                              self.targets)

        return self

    def dump(self) -> dict:
        """Return a hash representing this object."""
        out = {}
        out["input"] = {"portfolio": self.initial_portfolio.dump(),
                        "targets": self.targets.dump(),
                        "transactions_config": self.transactions_config.dump(),
                        "balance": self.initial_portfolio.balance(self.targets)}
        if self.final_portfolio:
            transactions_out = [x.dump() for x in self.transactions]
            out["output"] = {"portfolio": self.final_portfolio.dump(),
                             "transactions": transactions_out,
                             "balance": self.final_portfolio.balance(self.targets)}
        return out
