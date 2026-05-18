from target_tiller import Portfolio, Targets


class TestTargets:
    def test_all(self):
        targets = Targets({"IBM": 0.4,
                           "SGI": 0.6})
        assert targets.weight("SGI") == 0.6
        assert set(targets.symbols) == {"IBM", "SGI"}

        portfolio = Portfolio({"IBM": 1000,
                               "DELL": 2000})

        filtered = targets.filter_portfolio(portfolio)
        assert filtered.dump_holdings() == {"IBM": 1000,
                                            "SGI": 0}
