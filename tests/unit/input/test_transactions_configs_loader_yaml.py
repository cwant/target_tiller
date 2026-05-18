import os

from target_tiller import TransactionsConfig
from target_tiller.input import TransactionsConfigsLoaderYAML


class TestTransactionsConfigsLoaderYAML:
    def test_all(self):
        dir_path = os.path.dirname(__file__)
        fixtures_path = dir_path + "/../../fixtures"
        file_name = f"{fixtures_path}/fake_transactions_configs.yaml"
        transactions_configs_loader = TransactionsConfigsLoaderYAML(file_name)

        # Should be private?
        config = [{"portfolio_name": "90120XYZ",
                   "nickname": "Nest Egg",
                   "amount": 3000,
                   "action": "buy_only"},
                  {"portfolio_name": "12345ABC",
                   "nickname": "In the mattress",
                   "amount": 0,
                   "action": "buy_sell"}]
        assert transactions_configs_loader.config == config

        transactions_configs = [TransactionsConfig(**config[0]),
                                TransactionsConfig(**config[1])]

        assert transactions_configs_loader.transactions_configs == transactions_configs
