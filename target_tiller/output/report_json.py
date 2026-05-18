"""This module defines the ReportJSON class"""

import json
from typing import TYPE_CHECKING

from .reporter import Reporter

if TYPE_CHECKING:
    from ..transactions_calculator import TransactionsCalculator


class ReportJSON(Reporter):
    """A class to report information about portfolio rebalances via
    one of more TransactionCalculator instances. The output is
    formatted as JSON.
    """

    @property
    def output(self) -> dict:
        """This method contains the output rendered thus far,
        as a nested structure of lists or dicts.
        """
        if len(self._output) == 1:
            return self._output[0]
        return self._output

    @property
    def output_txt(self) -> str:
        """This method contains the output rendered thus far,
        as text rendered as JSON.
        """
        return json.dumps(self.output)

    def reset_output(self) -> None:
        """Reset the output for this instance."""
        self._output = []

    def render_report(self,
                      transactions_calculator: "TransactionsCalculator",
                      portfolio_filename: str | None = None) -> None:
        """Write a  report to our internal output buffer.
        (Do not actually return rendered text/output.)
        """
        out = transactions_calculator.dump()
        if portfolio_filename:
            out["portfolio_filename"] = portfolio_filename
        self.append(out)

    def report(self,
               transactions_calculator: "TransactionsCalculator",
               portfolio_filename: str | None = None) -> None:
        """Render and print the JSON report."""
        self.render_report(transactions_calculator,
                           portfolio_filename=portfolio_filename)

        print(self.output_txt)

    def append(self, data: dict) -> None:
        """Add information to the output buffer."""
        self._output.append(data)
