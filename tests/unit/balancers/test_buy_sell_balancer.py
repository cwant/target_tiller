import os

import pytest

from target_tiller import Portfolio, Targets, TransactionsConfig
from target_tiller.balancers import BuySellBalancer
from target_tiller.input import TargetsLoaderYAML, TDPortfolioLoaderCSV


class TestBuySellBalancer:
    # TODO: tests where things are constrained by minimum/maximum purchases

    def test_init_options(self):
        portfolio = Portfolio({})
        targets = Targets({})

        transactions_config = TransactionsConfig(**{"action": "buy_sell"},
                                                 amount=-100)
        balancer = BuySellBalancer(portfolio=portfolio,
                                    targets=targets,
                                    transactions_config=transactions_config)
        assert balancer

        transactions_config = TransactionsConfig(**{"action": "buy_sell"},
                                                 amount=100)
        balancer = BuySellBalancer(portfolio=portfolio,
                                   targets=targets,
                                   transactions_config=transactions_config)
        assert balancer

        transactions_config = TransactionsConfig(**{"action": "buy_sell"},
                                                 amount=-100)
        balancer = BuySellBalancer(portfolio=portfolio,
                                   targets=targets,
                                   transactions_config=transactions_config)
        assert balancer

        with pytest.raises(ValueError, match=r".*portfolio.*must.*provided.*"):
            balancer = BuySellBalancer(targets=targets,
                                        transactions_config=transactions_config)

        with pytest.raises(ValueError, match=r".*targets.*must.*provided.*"):
            balancer = BuySellBalancer(portfolio=portfolio,
                                        transactions_config=transactions_config)

        with pytest.raises(ValueError,
                           match=r".*transactions.*config.*must.*provided.*"):
            balancer = BuySellBalancer(portfolio=portfolio,
                                        targets=targets)

            transactions_config = TransactionsConfig(**{"action": "buy_sell"},
                                                     amount=100)
            balancer = BuySellBalancer(portfolio=portfolio,
                                       targets=targets,
                                       transactions_config=transactions_config)

    def test_all1(self):
        dir_path = os.path.dirname(__file__)
        fixtures_path = dir_path + "/../../fixtures"
        portfolio_loader = \
            TDPortfolioLoaderCSV(fixtures_path + "/fake_td_portfolio.csv")
        targets_loader = TargetsLoaderYAML(fixtures_path + "/fake_targets.yaml")

        portfolio = portfolio_loader.portfolio
        targets = targets_loader.targets

        transactions_config = TransactionsConfig(amount=-30000,
                                                 minimum_transaction=1000.0,
                                                 maximum_transaction=20000.0,
                                                 action="buy_sell")

        balancer = BuySellBalancer(portfolio=portfolio,
                                   targets=targets,
                                   transactions_config=transactions_config)

        assert balancer.minimum_transaction == 1000.0
        assert balancer.maximum_transaction == 20000.0

        assert portfolio.dump_holdings() == {"WTF": 25000.0,
                                             "LOL": 15000.0,
                                             "HUH": 30000.0,
                                             "WHY": 10000.0}

        assert set(targets.symbols) == {"WTF", "LOL", "HUH"}
        assert targets.weight("WTF") == 0.4
        assert targets.weight("LOL") == 0.35
        assert targets.weight("HUH") == 0.25

        assert balancer.value == 70000.0
        assert balancer.holding("WTF").value == 25000.0

        assert balancer.multiplier(["WTF", "LOL", "HUH"]) == 1.0
        # 1 / (0.35 + 0.25)
        assert balancer.multiplier(["LOL", "HUH"]) == 1.0 / 0.6

        assert balancer.current_total_value(["WTF", "LOL", "HUH"]) == 70000.0
        # We are spending 300000.0, so ...
        assert balancer.next_total_value(["WTF", "LOL", "HUH"]) == 40000.0

        # With the minimum purchase, we can only buy two of the holdings
        # This is because we are holding too much "HUH" (want to hold only 0.25)
        assert set(balancer.get_transaction_symbols(["WTF", "LOL", "HUH"])) == \
            {"WTF", "LOL", "HUH"}

        next_portfolio = balancer.run()

        multiplier = balancer.multiplier(["LOL", "WTF", "HUH"])
        assert multiplier == 1.0

        wtf_weight = 0.4 * multiplier
        lol_weight = 0.35 * multiplier
        huh_weight = 0.25 * multiplier

        # Next value of only the two holdings we are buying
        assert balancer.next_total_value(["WTF", "LOL", "HUH"]) == 40000.0

        # Should "WHY" have been copied over too?
        assert next_portfolio.dump_holdings() == {"WTF": 40000.0 * wtf_weight,
                                                  "LOL": 40000.0 * lol_weight,
                                                  "HUH": 40000.0 * huh_weight}

        assert round(next_portfolio.holding("WTF").value, 5) == 16000.0
        assert round(next_portfolio.holding("LOL").value, 5) == 14000.0
        assert round(next_portfolio.holding("HUH").value, 5) == 10000.0

        assert portfolio.balance(targets) < 0.8
        assert next_portfolio.balance(targets) == 1.0

    def test_all2(self):
        # Easy math: the final state matches targets perfectly

        portfolio = Portfolio({"WTF": 2500.0,
                               "LOL": 1500.0,
                               "HUH": 3000.0,
                               "WHY": 1000.0},
                              cash=10000.0, name="An account")

        targets = Targets({"WTF": 0.40,
                           "LOL": 0.50,
                           "NGL": 0.10})

        transactions_config = TransactionsConfig(portfolio_name="An account",
                                                 nickname="My nest egg",
                                                 action="buy_sell",
                                                 amount=-2200.0)

        balancer = BuySellBalancer(portfolio=portfolio,
                                   targets=targets,
                                   transactions_config=transactions_config)

        assert balancer.minimum_transaction == 100.0
        assert balancer.maximum_transaction == 10000.0

        assert portfolio.dump_holdings() == {"WTF": 2500.0,
                                             "LOL": 1500.0,
                                             "NGL": 0.0,
                                             "HUH": 3000.0,
                                             "WHY": 1000.0}

        assert set(targets.symbols) == {"WTF", "LOL", "NGL"}
        assert targets.weight("WTF") == 0.4
        assert targets.weight("LOL") == 0.50
        assert targets.weight("NGL") == 0.10

        assert balancer.value == 4000.0
        assert balancer.holding("WTF").value == 2500.0

        assert balancer.multiplier(["WTF", "LOL", "NGL"]) == 1.0

        assert balancer.current_total_value(["WTF", "LOL", "NGL"]) == 4000.0
        # We are selling 2000.0, so ...
        assert balancer.next_total_value(["WTF", "LOL", "NGL"]) == 1800.0

        assert set(balancer.get_transaction_symbols(["WTF", "LOL", "NGL"])) == \
            {"WTF", "LOL", "NGL"}

        next_portfolio = balancer.run()

        multiplier = balancer.multiplier(["LOL", "WTF", "NGL"])
        assert multiplier == 1.0

        # Next value of only the two holdings we are buying
        assert balancer.next_total_value(["WTF", "LOL", "NGL"]) == 1800.0

        # Should "WHY", "HUH" have been copied over too?
        assert next_portfolio.dump_holdings() == {"WTF": 720.0,
                                                  "LOL": 900.0,
                                                  "NGL": 180.0}

        assert portfolio.balance(targets) < 0.8
        assert next_portfolio.balance(targets) == 1.0
