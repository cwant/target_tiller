import os

from target_tiller.input import TDPortfolioLoaderCSV


class TestTDPortfolioLoaderCSV:
    def test_all(self):
        dir_path = os.path.dirname(__file__)
        fixtures_path = dir_path + "/../../fixtures"
        portfolio_loader = \
            TDPortfolioLoaderCSV(fixtures_path + "/fake_td_portfolio.csv")
        assert (portfolio_loader.cash == 20000)
        assert (portfolio_loader.name == "TD Direct Investing")

        portfolio = portfolio_loader.portfolio
        assert (portfolio.cash == 20000.0)
        assert (portfolio.name == "TD Direct Investing")
        assert (portfolio.dump_holdings() == {"WTF": 25000.0,
                                              "LOL": 15000.0,
                                              "HUH": 30000.0,
                                              "WHY": 10000.0})
