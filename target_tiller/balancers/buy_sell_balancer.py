"""This module defines the BuySellBalancer class"""

from .balancer import Balancer


class BuySellBalancer(Balancer):
    """A portfolio rebalancer that buys and sells to move towards targets."""

    def _transaction_modes(self) -> list:
        return ["buy", "sell"]
