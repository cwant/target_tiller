import json

import pytest

from target_tiller.cli import CLI
from target_tiller.input import FilesHelper


class TestCLI:
    def test_demo(self, capsys):
        cli = CLI(["--demo"])
        cli.run()
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert len(parsed) == 3
        assert "input" in parsed[0]
        assert "output" in parsed[0]
        assert "portfolio_filename" in parsed[0]

    def test_args(self, capsys):
        files_helper = FilesHelper("demo")

        with pytest.raises(ValueError) as error:
            cli = CLI([])
            cli.run()
        assert "No targets file" in str(error.value)

        with pytest.raises(ValueError) as error:
            cli = CLI(["--targets",
                       files_helper.targets_file])
            cli.run()
        assert "No transactions configs" in str(error.value)

        with pytest.raises(ValueError) as error:
            cli = CLI(["--targets",
                       files_helper.targets_file,
                       "--transactions-configs",
                       files_helper.transactions_configs_file])
            cli.run()
        assert "No portfolio files" in str(error.value)

        # This should just work
        cli = CLI(["--targets",
                   files_helper.targets_file,
                   "--transactions-configs",
                   files_helper.transactions_configs_file,
                   "--portfolios",
                   files_helper.portfolio_files[0],
                   "--portfolios",
                   files_helper.portfolio_files[1],
                   "--portfolios",
                   files_helper.portfolio_files[2]])
        cli.run()

        # This should not
        with pytest.raises(FileNotFoundError) as error:
            cli = CLI(["--targets",
                       "foo-i-dont-exist.yaml",
                       "--transactions-configs",
                       files_helper.transactions_configs_file,
                       "--portfolios",
                       files_helper.portfolio_files[0],
                       "--portfolios",
                       files_helper.portfolio_files[1],
                       "--portfolios",
                       files_helper.portfolio_files[2]])
            cli.run()
        assert "No such file" in str(error.value)
