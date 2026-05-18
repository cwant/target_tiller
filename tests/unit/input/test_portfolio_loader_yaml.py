import os

from target_tiller.input import PortfolioLoaderYAML


class TestPortfolioLoaderYAML:
    def test_all(self):
        dir_path = os.path.dirname(__file__)
        fixtures_path = dir_path + "/../../fixtures"
        portfolio_loader = PortfolioLoaderYAML(fixtures_path + "/fake_portfolio.yaml")
        assert (portfolio_loader.cash == 20000)
        assert (portfolio_loader.name == "My Account")

        portfolio = portfolio_loader.portfolio
        assert (portfolio.cash == 20000.0)
        assert (portfolio.name == "My Account")
        assert (portfolio.dump_holdings() == {"WTF": 25000.0,
                                              "LOL": 15000.0,
                                              "HUH": 30000.0,
                                              "WHY": 10000.0})
