"""This module defines the CLI class"""

import argparse
import sys

from . import TransactionsCalculator, __version__
from .input import (
    FilesHelper,
    PortfolioLoaderYAML,
    TargetsLoaderYAML,
    TDPortfolioLoaderCSV,
    TransactionsConfigsLoaderYAML,
)
from .output import ReportHTML, ReportJSON


class CLI:
    """This class runs the CLI (command line interface) program."""

    def __init__(self, argv: list | None = None) -> None:
        if argv is None:
            argv = []

        self._options = self._process_options(argv)

        if self._options["version"]:
            print(__version__)
            sys.exit(0)

        self._initialize_reporter()

    def run(self) -> None:
        """Run the rebalancing of the portfolio(s)."""
        self._gather_inputs()
        self._calculate()
        self._render_output()

    @property
    def targets_file(self) -> str:
        """Get the target filename."""
        return self._options.get("targets")

    @property
    def transactions_configs_file(self) -> str:
        """Get the transactions configs filename."""
        return self._options.get("transactions_configs")

    @property
    def portfolio_files(self) -> list:
        """Get the portfolio filenames."""
        return self._options.get("portfolios")

    def _initialize_reporter(self) -> None:
        if self._options["output_format"] == "html":
            self._reporter = ReportHTML()
        else:
            self._reporter = ReportJSON()

    def _process_options(self, argv: list | None = None) -> dict:
        if argv is None:
            argv = []

        parser = argparse.ArgumentParser()
        parser.add_argument("--version", action="store_true")
        parser.add_argument("--demo",
                            action="store_true",
                            help="Run the program with demo files")
        parser.add_argument("--transactions-configs")
        parser.add_argument("--targets")
        parser.add_argument("--portfolios", action="append")
        parser.add_argument("-o", "--output-format",
                            choices=["json", "html"], default="json")

        return vars(parser.parse_args(argv))

    def _gather_inputs(self) -> None:
        if self._options.get("demo"):
            files_helper = FilesHelper("demo")
            self._options["targets"] = files_helper.targets_file
            self._options["transactions_configs"] = \
                files_helper.transactions_configs_file
            self._options["portfolios"] = files_helper.portfolio_files
        if not self.targets_file:
            raise ValueError("No targets file specified.")
        if not self.transactions_configs_file:
            raise ValueError("No transactions configs file specified.")
        if not self.portfolio_files:
            raise ValueError("No portfolio files specified.")

    def _calculate(self) -> None:
        self._reporter.reset_output()

        targets_loader = TargetsLoaderYAML(self.targets_file)
        transactions_configs_loader = \
            TransactionsConfigsLoaderYAML(self.transactions_configs_file)

        targets = targets_loader.targets
        transactions_configs = transactions_configs_loader.transactions_configs

        # Hash the portfolios by name because the transactions_configs
        # needs to find them by name
        portfolio_loaders = {}
        for filename in self.portfolio_files:
            if filename[-4:] == ".csv":
                portfolio_loader = TDPortfolioLoaderCSV(filename)
            else:
                portfolio_loader = PortfolioLoaderYAML(filename)
            portfolio_loaders[portfolio_loader.name] = portfolio_loader

        for transactions_config in transactions_configs:
            portfolio_loader = portfolio_loaders[transactions_config.portfolio_name]
            portfolio = portfolio_loader.portfolio
            transactions_calculator = \
                TransactionsCalculator(portfolio=portfolio,
                                       targets=targets,
                                       transactions_config=transactions_config).run()

            self._reporter.render_report(transactions_calculator,
                                         portfolio_filename=portfolio_loader.filename)

    def _render_output(self) -> None:
        print(self._reporter.output_txt)
