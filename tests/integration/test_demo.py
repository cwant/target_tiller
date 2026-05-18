# This is essentially the first cell of the demo notebook

import re

from target_tiller import TransactionsCalculator
from target_tiller.input import (
    FilesHelper,
    PortfolioLoaderYAML,
    TargetsLoaderYAML,
    TDPortfolioLoaderCSV,
    TransactionsConfigsLoaderYAML,
)
from target_tiller.output import ReportHTML, ReportJSON


class TestDemo:
    def test_all(self):
        files_helper = FilesHelper("demo")

        targets_loader = TargetsLoaderYAML(files_helper.targets_file)
        transactions_configs_loader = \
            TransactionsConfigsLoaderYAML(files_helper.transactions_configs_file)

        targets = targets_loader.targets
        assert set(targets.symbols) == {"LOL", "HUH", "WHY"}
        assert targets.weight("LOL") == 0.2
        assert targets.weight("HUH") == 0.3
        assert targets.weight("WHY") == 0.5

        # Hash by portfolio name
        transactions_configs = \
            {transaction_config.portfolio_name: transaction_config for \
             transaction_config in transactions_configs_loader.transactions_configs}

        # Hash the portfolios by name because the transactions_configs
        # needs to find them by name
        portfolio_loaders = {}

        for filename in files_helper.portfolio_files:
            if filename[-4:] == ".csv":
                portfolio_loader = TDPortfolioLoaderCSV(filename)
            else:
                portfolio_loader = PortfolioLoaderYAML(filename)
            portfolio_loaders[portfolio_loader.name] = portfolio_loader

        portfolio_names = {"ABC123", "XYZ987", "ABBA90210"}
        assert set(portfolio_loaders.keys()) == portfolio_names
        assert set(transactions_configs.keys()) == portfolio_names

        reporter_html = ReportHTML()
        reporter_json = ReportJSON()
        assert len(reporter_html.output) == 0
        assert len(reporter_json.output) == 0

        # ABC123, portfolio1.yaml, buy_only, amount 1000.0

        portfolio_loader = portfolio_loaders["ABC123"]
        portfolio = portfolio_loader.portfolio
        transactions_config = transactions_configs["ABC123"]
        assert transactions_config.portfolio_name == "ABC123"
        assert transactions_config.action == "buy_only"
        assert transactions_config.amount == 1000.0

        assert set(portfolio.symbols) == {"LOL", "HUH", "WHY", "FUN", "NGL"}
        assert portfolio.holding("LOL").value == 500.0
        assert portfolio.holding("HUH").value == 500.0
        assert portfolio.holding("WHY").value == 600.0
        assert portfolio.holding("FUN").value == 100.0
        assert portfolio.holding("NGL").value == 1000.0

        transactions_calculator = \
            TransactionsCalculator(portfolio=portfolio,
                                   targets=targets,
                                   transactions_config=transactions_config).run()

        final_portfolio = transactions_calculator.final_portfolio
        assert final_portfolio.holding("LOL").value == 500.0
        assert final_portfolio.holding("HUH").value == 787.5
        assert final_portfolio.holding("WHY").value == 1312.5
        assert final_portfolio.holding("FUN").value == 100.0
        assert final_portfolio.holding("NGL").value == 1000.0

        # Hash by symbol
        transactions = {transaction.symbol: transaction for \
                        transaction in transactions_calculator.transactions}
        assert set(transactions.keys()) == {"LOL", "HUH", "WHY"}
        assert transactions["LOL"].action == "Hold"
        assert transactions["LOL"].amount is None
        assert transactions["HUH"].action == "Buy"
        assert transactions["HUH"].amount == 287.5
        assert transactions["WHY"].action == "Buy"
        assert transactions["WHY"].amount == 712.5

        assert round(portfolio.balance(targets), 3) == 0.831
        assert round(final_portfolio.balance(targets), 3) == 0.990

        change = final_portfolio.holdings_value - portfolio.holdings_value
        assert change == 1000.0

        reporter_html.render_report(transactions_calculator,
                                    portfolio_filename=portfolio_loader.filename)
        reporter_json.render_report(transactions_calculator,
                                    portfolio_filename=portfolio_loader.filename)

        # XYZ987, portfolio2.yaml, sell_only, amount -3000.0

        portfolio_loader = portfolio_loaders["XYZ987"]
        portfolio = portfolio_loader.portfolio
        transactions_config = transactions_configs["XYZ987"]
        assert transactions_config.portfolio_name == "XYZ987"
        assert transactions_config.action == "sell_only"
        assert transactions_config.amount == -3000.0

        assert set(portfolio.symbols) == {"LOL", "HUH", "WHY", "FUN", "NGL"}
        assert portfolio.holding("LOL").value == 5000.0
        assert portfolio.holding("HUH").value == 4000.0
        assert portfolio.holding("WHY").value == 3000.0
        assert portfolio.holding("FUN").value == 12000.0
        assert portfolio.holding("NGL").value == 800.0

        transactions_calculator = \
            TransactionsCalculator(portfolio=portfolio,
                                   targets=targets,
                                   transactions_config=transactions_config).run()

        final_portfolio = transactions_calculator.final_portfolio
        assert final_portfolio.holding("LOL").value == 2400.0
        assert final_portfolio.holding("HUH").value == 3600.0
        assert final_portfolio.holding("WHY").value == 3000.0
        assert final_portfolio.holding("FUN").value == 12000.0
        assert final_portfolio.holding("NGL").value == 800.0

        # Hash by symbol
        transactions = {transaction.symbol: transaction for \
                        transaction in transactions_calculator.transactions}
        assert set(transactions.keys()) == {"LOL", "HUH", "WHY"}
        assert transactions["LOL"].action == "Sell"
        assert transactions["LOL"].amount == 2600.0
        assert transactions["HUH"].action == "Sell"
        assert transactions["HUH"].amount == 400.0
        assert transactions["WHY"].action == "Hold"
        assert transactions["WHY"].amount is None

        assert round(portfolio.balance(targets), 3) == 0.668
        assert round(final_portfolio.balance(targets), 3) == 0.795

        change = final_portfolio.holdings_value - portfolio.holdings_value
        assert change == -3000.0

        reporter_html.render_report(transactions_calculator,
                                    portfolio_filename=portfolio_loader.filename)
        reporter_json.render_report(transactions_calculator,
                                    portfolio_filename=portfolio_loader.filename)

        # ABBA90210, portfolio3.yaml, buy_sell, amount 0.0

        portfolio_loader = portfolio_loaders["ABBA90210"]
        portfolio = portfolio_loader.portfolio
        transactions_config = transactions_configs["ABBA90210"]

        assert set(portfolio.symbols) == {"LOL", "HUH", "WHY", "FUN", "NGL"}
        assert portfolio.holding("LOL").value == 5000.0
        assert portfolio.holding("HUH").value == 5000.0
        assert portfolio.holding("WHY").value == 5000.0
        assert portfolio.holding("FUN").value == 5000.0
        assert portfolio.holding("NGL").value == 5000.0

        transactions_calculator = \
            TransactionsCalculator(portfolio=portfolio,
                                   targets=targets,
                                   transactions_config=transactions_config).run()

        final_portfolio = transactions_calculator.final_portfolio
        assert final_portfolio.holding("LOL").value == 3000.0
        assert final_portfolio.holding("HUH").value == 4500.0
        assert final_portfolio.holding("WHY").value == 7500.0
        assert final_portfolio.holding("FUN").value == 5000.0
        assert final_portfolio.holding("NGL").value == 5000.0

        # Hash by symbol
        transactions = {transaction.symbol: transaction for \
                        transaction in transactions_calculator.transactions}
        assert set(transactions.keys()) == {"LOL", "HUH", "WHY"}
        assert transactions["LOL"].action == "Sell"
        assert transactions["LOL"].amount == 2000.0
        assert transactions["HUH"].action == "Sell"
        assert transactions["HUH"].amount == 500.0
        assert transactions["WHY"].action == "Buy"
        assert transactions["WHY"].amount == 2500.0

        assert round(portfolio.balance(targets), 3) == 0.784
        assert round(final_portfolio.balance(targets), 3) == 1.000

        change = final_portfolio.holdings_value - portfolio.holdings_value
        assert change == 0.0

        reporter_html.render_report(transactions_calculator,
                                    portfolio_filename=portfolio_loader.filename)
        reporter_json.render_report(transactions_calculator,
                                    portfolio_filename=portfolio_loader.filename)

        assert len(reporter_html.output) > 0
        pattern = re.compile(".*Account.*ABC123.*"\
                             "Initial portfolio.*Balance.*83.1%.*"\
                             "Transactions.*spent.*1,000.00.*"\
                             "Final portfolio.*Balance.*99.0%.*"\
                             ".*Account.*XYZ987.*"\
                             "Initial portfolio.*Balance.*66.8%.*"\
                             "Transactions.*withdrew.*3,000.00.*"\
                             "Final portfolio.*Balance.*79.5%.*"\
                             ".*Account.*ABBA90210.*"\
                             "Initial portfolio.*Balance.*78.4%.*"\
                             "Transactions.*spent.*0.00.*"\
                             "Final portfolio.*Balance.*100.0%.*",
                             re.DOTALL)
        assert pattern.match(reporter_html.output) is not None

        assert len(reporter_json.output) == 3

        assert reporter_json.output[0]["input"]["portfolio"]["name"] == "ABC123"
        assert round(reporter_json.output[0]["input"]["balance"], 3) == 0.831
        assert round(reporter_json.output[0]["output"]["balance"], 3) == 0.990

        assert reporter_json.output[1]["input"]["portfolio"]["name"] == "XYZ987"
        assert round(reporter_json.output[1]["input"]["balance"], 3) == 0.668
        assert round(reporter_json.output[1]["output"]["balance"], 3) == 0.795

        assert reporter_json.output[2]["input"]["portfolio"]["name"] == "ABBA90210"
        assert round(reporter_json.output[2]["input"]["balance"], 3) == 0.784
        assert round(reporter_json.output[2]["output"]["balance"], 3) == 1.000
