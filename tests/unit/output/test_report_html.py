import re

from target_tiller import Portfolio, Targets, TransactionsCalculator, TransactionsConfig
from target_tiller.output import ReportHTML


class TestReportHTML:
    # We test as much as we can, but display() depends on Jupyter

    def test_all(self):
        portfolio = Portfolio({"WTF": 2500.0,
                               "LOL": 1500.0,
                               "HUH": 3000.0,
                               "WHY": 1000.0},
                              cash=20000, name="An account")

        targets = Targets({"WTF": 0.40,
                           "LOL": 0.50,
                           "NGL": 0.10})


        transactions_config = TransactionsConfig(portfolio_name="An account",
                                                 nickname="My nest egg",
                                                 action="buy_only",
                                                 amount=6000.0)

        transactions_calculator = TransactionsCalculator(portfolio,
                                                         targets,
                                                         transactions_config)

        transactions_calculator.run()

        reporter = ReportHTML()
        assert reporter.output == ""

        reporter.append("Hey you!")
        assert reporter.output == "Hey you!"
        reporter.append("Hey you!")
        assert reporter.output == "Hey you!Hey you!"

        reporter.reset_output()
        assert reporter.output == ""

        reporter.render_report(transactions_calculator,
                               portfolio_filename="docs/my_portfolio.yaml")

        # Basic structure
        pattern = re.compile(".*<h1>Account: An account.*</h1>.*"\
                             "<h2>Initial portfolio</h2>.*"\
                             "<h2>Transactions.*</h2>.*"\
                             "<h2>Final portfolio</h2>.*",
                             re.DOTALL)

        assert pattern.match(reporter.output) is not None

        # TODO: add more ...
