"""This module defines the ReportHTML class"""

from typing import TYPE_CHECKING

from IPython.display import HTML, display

from .report_html import ReportHTML

if TYPE_CHECKING:
    from ..transactions_calculator import TransactionsCalculator


class ReportJupyter(ReportHTML):
    """A class to report information about portfolio rebalances via
    one of more TransactionCalculator instances. The output is
    formatted as HTML for use in Jupyter notebooks.
    """
    def display(self) -> None:
        """Display the output as HTML in a jupyter notebook cell."""
        # pylint: disable=import-outside-toplevel
        # We don't want the entire class to depend on Jupyter
        display(HTML(self.output_txt))
        # Needed?
        self.reset_output()

    def report(self, transactions_calculator: "TransactionsCalculator",
               portfolio_filename: str | None = None) -> None:
        """Render and display the HTML report in a Jupyter notebook cell."""
        self.render_report(transactions_calculator, portfolio_filename)
        self.display()
