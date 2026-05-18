import math

from target_tiller import Portfolio, Targets


class TestPortfolio:
    def test_all(self):
        holdings = {"WTF": 25000.0,
                    "LOL": 15000.0,
                    "HUH": 30000.0,
                    "WHY": 10000.0}
        cash = 20000
        name = "An account"
        portfolio = Portfolio(holdings, cash=cash, name=name)

        assert portfolio.cash == 20000.0
        assert portfolio.name == "An account"
        assert portfolio.dump_holdings() == {"WTF": 25000.0,
                                             "LOL": 15000.0,
                                             "HUH": 30000.0,
                                             "WHY": 10000.0}

        portfolio2 = Portfolio({"WTF": 1000.0,
                                "TIL": 4000.0}, 1000.0)
        portfolio3 = portfolio.merge(portfolio2)

        assert set(portfolio3.symbols) == {"WTF", "LOL", "HUH", "WHY", "TIL"}
        # WTF is value from portfolio, not portfolio2
        assert portfolio3.dump_holdings() == {"WTF": 25000.0,
                                              "LOL": 15000.0,
                                              "HUH": 30000.0,
                                              "WHY": 10000.0,
                                              "TIL": 4000.0}
        # cash, name are values from portfolio, not portfolio2
        assert portfolio3.cash == 20000.0
        assert portfolio3.name == "An account"

        targets = Targets({"WTF": 0.40,
                           "LOL": 0.50,
                           "NGL": 0.10})

        # Mutable!
        portfolio.include_empty_targets(targets)
        assert portfolio.dump_holdings() == { "WTF": 25000.0,
                                              "LOL": 15000.0,
                                              "HUH": 30000.0,
                                              "WHY": 10000.0,
                                              "NGL": 0.0 }

        # WTF (25000.0) + LOL (15000.0) + NG (0.0)
        assert portfolio.targeted_value(targets) == 40000.0
        # Total value of holdings only ...
        assert portfolio.holdings_value == 80000.0

        # targeted_value divided by total value of holdings
        assert portfolio.targeted_proportion(targets) == 0.5

        # Include cash ...
        assert portfolio.total_value == 100000.0

        # targeted_value divided by total value including cash
        assert portfolio.targeted_proportion_including_cash(targets) == 0.4

        # Distance from ideal targets ...
        distance2_wtf = (25000.0 / 40000.0 - 0.40)**2
        distance2_lol = (15000.0 / 40000.0 - 0.50)**2
        distance2_ngl = (0.0 / 40000.0 - 0.10)**2
        distance = math.sqrt(distance2_wtf + distance2_lol + distance2_ngl)
        assert portfolio.balance(targets) == 1.0 - distance

        # weight of holding versus all holdings (cash not included)
        # WHY (10000) / total (80000.0)
        assert portfolio.weight("WHY") == 1 / 8

        # Some corner cases
        assert portfolio.targeted_value(None) is None
        assert portfolio.targeted_proportion(None) is None
        assert portfolio.targeted_proportion_including_cash(None) is None
        assert portfolio.holding("HAMBURGER") == 0
        assert portfolio.weight("HAMBURGER") == 0
        portfolio4 = Portfolio({})
        assert portfolio4.targeted_proportion(targets) == 0
        portfolio4.name = "Set the name"
        assert portfolio4.name == "Set the name"
        portfolio5 = Portfolio({"LOL": 0})
        assert list(portfolio5.symbols) == ["LOL"]
        assert portfolio4.holdings_value == 0
        assert portfolio4.weight("LOL") == 0
