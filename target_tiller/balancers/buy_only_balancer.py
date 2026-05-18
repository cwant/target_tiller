"""This module defines the BuyOnlyBalancer class"""

from .balancer import Balancer


class BuyOnlyBalancer(Balancer):
    """A portfolio rebalancer that only buys to move towards targets."""

    def _transaction_modes(self) -> list:
        return ["buy"]
