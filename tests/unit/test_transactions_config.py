import pytest

from target_tiller import TransactionsConfig
from target_tiller.balancers import BuyOnlyBalancer, BuySellBalancer, SellOnlyBalancer


class TestTransactionsConfig:
    # TODO: tests where things are constrained by minimum/maximum purchases

    def test_buy_only_init_options(self):
        transactions_config = TransactionsConfig(**{"action": "buy_only",
                                                    "amount": 40})
        assert transactions_config

        with pytest.raises(ValueError, match=r".*[Mm]ust.*positive.*buying.*"):
            transactions_config = TransactionsConfig(**{"action": "buy_only",
                                                        "amount": 0})

        with pytest.raises(ValueError, match=r".*[Mm]ust.*positive.*buying.*"):
            transactions_config = TransactionsConfig(**{"action": "buy_only",
                                                        "amount": -20})
    def test_sell_only_init_options(self):
        transactions_config = TransactionsConfig(**{"action": "sell_only",
                                                    "amount": -40})
        assert transactions_config

        with pytest.raises(ValueError, match=r".*[Mm]ust.*negative.*selling.*"):
            transactions_config = TransactionsConfig(**{"action": "sell_only",
                                                        "amount": 0})

        with pytest.raises(ValueError, match=r".*[Mm]ust.*negative.*selling.*"):
            transactions_config = TransactionsConfig(**{"action": "sell_only",
                                                        "amount": 20})
    def test_buy_sell_init_options(self):
        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "amount": -40})
        assert transactions_config

        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "amount": 0})
        assert transactions_config

        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "amount": 20})
        assert transactions_config

    def test_bad_action_init_options(self):
        with pytest.raises(ValueError, match=r".*not.*valid.*action.*"):
            TransactionsConfig(**{"action": "dunno"})

    def test_portfolio_name(self):
        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "amount": 20})
        assert transactions_config.portfolio_name is None

        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "amount": 20,
                                                    "portfolio_name": "nest egg"})
        assert transactions_config.portfolio_name == "nest egg"

    def test_nickname(self):
        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "amount": 20})
        assert transactions_config.nickname is None

        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "amount": 20,
                                                    "nickname": "hot moola"})
        assert transactions_config.nickname == "hot moola"


    def test_action(self):
        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "amount": 20})
        assert transactions_config.action == "buy_sell"

    def test_amount(self):
        # Default: 0
        transactions_config = TransactionsConfig(**{"action": "buy_sell"})
        assert transactions_config.amount == 0

        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "amount": 20})
        assert transactions_config.amount == 20

    def test_minimum_transaction(self):
        # Default: 100
        transactions_config = TransactionsConfig(**{"action": "buy_sell"})
        assert transactions_config.minimum_transaction == 100

        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "minimum_transaction": 2000})
        assert transactions_config.minimum_transaction == 2000

    def test_maximum_transaction(self):
        # Default: 10000
        transactions_config = TransactionsConfig(**{"action": "buy_sell"})
        assert transactions_config.maximum_transaction == 10000

        transactions_config = TransactionsConfig(**{"action": "buy_sell",
                                                    "maximum_transaction": 2000})
        assert transactions_config.maximum_transaction == 2000

    def test_balancer_class(self):
        transactions_config = TransactionsConfig(**{"action": "buy_sell"})
        assert transactions_config.balancer_class == BuySellBalancer

        transactions_config = TransactionsConfig(**{"action": "buy_only",
                                                    "amount": 100})
        assert transactions_config.balancer_class == BuyOnlyBalancer

        transactions_config = TransactionsConfig(**{"action": "sell_only",
                                                    "amount": -100})
        assert transactions_config.balancer_class == SellOnlyBalancer

    def test_all(self):
        transactions_config = TransactionsConfig(portfolio_name="ABC123",
                                                 nickname="My nest egg",
                                                 action="buy_only",
                                                 amount=5000.0)
        assert transactions_config.portfolio_name == "ABC123"
        assert transactions_config.nickname == "My nest egg"
        assert transactions_config.action == "buy_only"
        assert transactions_config.amount == 5000.0
        # Defaults
        assert transactions_config.minimum_transaction == 100.0
        assert transactions_config.maximum_transaction == 10000.0

        assert transactions_config.balancer_class == BuyOnlyBalancer
