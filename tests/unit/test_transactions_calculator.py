from target_tiller import (
    Portfolio,
    Targets,
    Transaction,
    TransactionsCalculator,
    TransactionsConfig,
)


class TestTransactionsCalculator:
    def test_all(self):
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
                                                 action="buy_only",
                                                 amount=6000.0)

        transactions_calculator = TransactionsCalculator(portfolio,
                                                         targets,
                                                         transactions_config)

        transactions_calculator.run()
        assert transactions_calculator.initial_portfolio == portfolio

        final_portfolio = transactions_calculator.final_portfolio
        assert final_portfolio.dump_holdings() == {"WTF": 4000.0,
                                                   "LOL": 5000.0,
                                                   "NGL": 1000.0,
                                                   "HUH": 3000.0,
                                                   "WHY": 1000.0}

        transactions = [Transaction("WTF", "Buy", 1500),
                        Transaction("LOL", "Buy", 3500),
                        Transaction("NGL", "Buy", 1000)]

        assert set(transactions_calculator.transactions) == set(transactions)
