"""This module defines the TDPortfolioLoaderCSV class"""

import csv
from io import StringIO

from ..portfolio import Portfolio


class TDPortfolioLoaderCSV:
    """This is the format that TD Waterhouse (Canada) exports an
    account to.
    """

    NUM_ACCOUNT_NAME_PARTS = 2

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self._raw = None
        self._cash = None
        self._portfolio = None
        self._name = None

    def raw(self) -> dict:
        """The parsed parts of the file (loading as needed)."""
        if not self._raw:
            with open(self.filename, encoding="utf-8") as file:
                data = file.readlines()
            header_buffer = {}
            csv_buffer = ""
            do_header = True
            for line in data:
                if do_header:
                    if line == ",\n":
                        do_header = False
                    elif line[:6] == "Margin":
                        continue
                    else:
                        key, value = [x.strip() for x in line.split(",")]
                        header_buffer[key] = value
                else:
                    csv_buffer += line
            self._raw = {}
            self._raw["header"] = header_buffer
            self._raw["body"] = \
                csv.DictReader(StringIO(csv_buffer))
        return self._raw

    @property
    def name(self) -> str:
        """The name of the portfolio."""
        if not self._name:
            full_name = self.raw()["header"]["Account"]
            parts = full_name.split(" - ")
            if len(parts) < self.NUM_ACCOUNT_NAME_PARTS:
                self._name = full_name
            else:
                self._name = full_name.split(" - ")[1]

        return self._name

    @property
    def cash(self) -> float:
        """The cash held by the portfolio."""
        if not self._cash:
            self._cash = float(self.raw()["header"]["Cash"])

        return self._cash

    @property
    def portfolio(self) -> Portfolio:
        """The Portfolio object created by loading the file."""
        if not self._portfolio:
            dict_holdings = { row["Symbol"]: float(row["Market Value"]) \
                              for row in self.raw()["body"] }
            self._portfolio = Portfolio(dict_holdings, cash=self.cash, name=self.name)

        return self._portfolio
