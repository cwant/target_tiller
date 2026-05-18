"""This module defines the Reporter class"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..transactions_calculator import TransactionsCalculator


class Reporter:
    """Abstract class to report information about portfolio rebalances
    via one or more TransactionsCalculator instances.
    """

    def __init__(self) -> None:
        self.reset_output()

    @property
    def output(self) -> str | dict:
        """This method contains the output rendered thus far."""
        raise NotImplementedError

    @property
    def output_txt(self) -> str:
        """Text representation of output rendered thus far."""
        raise NotImplementedError

    def reset_output(self) -> None:
        """Reset the output for this instance."""
        raise NotImplementedError

    def render_report(self,
                      transactions_calculator: "TransactionsCalculator",
                      portfolio_filename: str | None = None) -> None:
        """Write a report to our internal output buffer.
        (Do not actually return rendered text/output.)
        """
        raise NotImplementedError

    def report(self,
               transactions_calculator: "TransactionsCalculator",
               portfolio_filename: str | None = None) -> None:
        """Render and print/write/display the report."""
        raise NotImplementedError

    def append(self, data: str | dict) -> None:
        """Add information to the output buffer."""
        raise NotImplementedError
