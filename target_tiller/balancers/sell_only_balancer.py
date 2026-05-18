"""This module defines the SellOnlyBalancer class"""

from .balancer import Balancer


class SellOnlyBalancer(Balancer):
    """A portfolio rebalancer that only sells to move towards targets."""

    def _transaction_modes(self) -> list:
        return ["sell"]
