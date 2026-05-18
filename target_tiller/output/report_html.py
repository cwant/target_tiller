"""This module defines the ReportHTML class"""

from pathlib import Path
from typing import TYPE_CHECKING

from .reporter import Reporter

if TYPE_CHECKING:
    from ..portfolio import Portfolio
    from ..targets import Targets
    from ..transactions_calculator import TransactionsCalculator


class ReportHTML(Reporter):
    """A class to report information about portfolio rebalances via
    one of more TransactionCalculator instances. The output is
    formatted as HTML.
    """

    def __init__(self) -> None:
        super().__init__()
        stylesheet_dir = Path(__file__).resolve().parent
        self.stylesheet = Path(stylesheet_dir, "target_tiller.css")

    @property
    def output(self) -> str:
        """This method contains the HTML output rendered thus far."""
        return self._output

    @property
    def output_txt(self) -> str:
        """This method contains the HTML output rendered thus far,
        including stylesheet definition
        """
        return self._generate_style() + self._output

    def reset_output(self) -> None:
        """Reset the output for this instance."""
        self._output = ""

    def append(self, data: str) -> None:
        """Add information to the output buffer."""
        self._output += data

    def _value_report(self, portfolio: "Portfolio") -> None:
        self.append("<p>Total investments value: "\
                    f"<b>${portfolio.holdings_value:,.2f}</b><br>"\
                    "Total cash value: "\
                    f"<b>${portfolio.cash:,.2f}</b><br>"\
                    "Total portfolio value: "\
                    f"<b>${portfolio.total_value:,.2f}</b><br></p>")

    def _generate_style(self) -> str:
        return f'<style>{open(self.stylesheet, encoding="utf-8").read()}'\
            '</style>\n'

    def render_report(self,
                      transactions_calculator: "TransactionsCalculator",
                      portfolio_filename: str | None = None) -> None:
        """Write a  report to our internal output buffer.
        (Do not actually return rendered text/output.)
        """
        initial_portfolio = transactions_calculator.initial_portfolio
        targets = transactions_calculator.targets
        initial_portfolio.include_empty_targets(targets)
        transactions_config = transactions_calculator.transactions_config
        portfolio_name = transactions_config.portfolio_name
        nickname = transactions_config.nickname
        net_change = transactions_config.amount
        final_portfolio = transactions_calculator.final_portfolio
        transactions = transactions_calculator.transactions

        self.append('<div class="rounded">\n')

        if nickname:
            self.append(f"\n<h1>Account: {portfolio_name} ({nickname})</h1>\n")
        else:
            self.append(f"\n<h1>Account: {portfolio_name}</h1>\n")

        transaction_type = "Spend" if (net_change >= 0) else "Withdrawal"

        comment = f"{transaction_type} amount: <b>${abs(net_change):,.2f}</b>"

        if portfolio_filename:
            comment = f"Filename: {portfolio_filename}<br>{comment}"

        self.append(f"<p>{comment}</p>\n")

        self._value_report(initial_portfolio)

        self.append("\n<h2>Initial portfolio</h2>\n")

        self._portfolio_report(initial_portfolio, targets)

        actual_change = final_portfolio.actual_change(initial_portfolio)
        final_portfolio.cash = initial_portfolio.cash - actual_change

        action = "spent" if (actual_change >= 0) else "withdrew"

        self.append(f"\n<h2>Transactions for {portfolio_name} "\
                    f"({action} \\${abs(actual_change):,.2f} "\
                    f"of \\${abs(net_change):,.2f})</h2>\n")
        self._transaction_report(transactions)

        self.append("\n<h2>Final portfolio</h2>\n")
        self._portfolio_report(final_portfolio, targets)
        self._value_report(final_portfolio)

        self.append("</div>\n")

    def report(self, transactions_calculator: "TransactionsCalculator",
               portfolio_filename: str | None = None) -> None:
        """Render the HTML report."""
        # For compatibility with Jupyter notebook reporter
        self.render_report(transactions_calculator, portfolio_filename)

    def _format_holding(self, symbol: str, portfolio: "Portfolio",
                        targeted_portfolio: "Portfolio | None" = None,
                        targets: "Targets | None" = None) -> str:
        buffer = "<tr>"
        buffer += f"<td><b>{symbol}</b></td>"
        buffer += f"<td>${portfolio.holding(symbol).value:,.2f}</td>"
        buffer += f"<td>{portfolio.weight(symbol):.1%}</td>"
        if targeted_portfolio and (symbol in targeted_portfolio.symbols):
            buffer += f"<td><b>{targeted_portfolio.weight(symbol):.1%}</b></td>"
        if targets and (symbol in targets.symbols):
            buffer += f"<td><b>{targets.weight(symbol):.1%}</b></td>"
        buffer += "</tr>"

        return buffer

    def _portfolio_report(self, portfolio: "Portfolio", targets: "Targets") -> None:
        targeted_portfolio = targets.filter_portfolio(portfolio)

        table = "<table>"
        table += "<tr>"\
            "<th>Symbol</th>"\
            "<th>Holding</th>"\
            "<th>Portfolio weight</th>"\
            "<th>Balanced weight</th>"\
            "<th>Target weight</th>"\
            "</tr>"
        for symbol in portfolio.symbols:
            table += self._format_holding(symbol,
                                          portfolio,
                                          targeted_portfolio,
                                          targets)
        table += "</table>\n"

        self.append(table)
        self.append("<p>Targeted value: "\
                    f"<b>${portfolio.targeted_value(targets):,.2f}</b><br>"\
                    "Targeted proportion: "\
                    f"<b>{portfolio.targeted_proportion(targets):.1%}</b> "\
                    "(including cash: "\
                    f"{portfolio.targeted_proportion_including_cash(targets):.1%})<br>"\
                    f"Balance: <b>{portfolio.balance(targets):.1%}</b></p>\n")

    def _transaction_report(self, transactions: list) -> None:
        table = "<table>"
        table += "<tr>"\
            "<th>Symbol</th>"\
            "<th>Action</th>"\
            "<th>Amount</th>"\
            "</tr>"
        for transaction in transactions:
            table += "<tr>"
            table += f"<td><b>{transaction.symbol}</b></td>"
            format_class = transaction.action.lower()
            table += f'<td class="{format_class}"><b>{transaction.action}</b></td>'

            if transaction.amount:
                table += f'<td class="{format_class}">${transaction.amount:,.2f}</td>'

            table += "</tr>"
        table += "</table>\n"

        self.append(table)
