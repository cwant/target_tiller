import os
from pathlib import Path
from unittest import mock

import pytest

from target_tiller.input import FilesHelper

# For mocking/patching os.path.exists to find the user files
# See methods mock_os_path_exists and test_user below
backup_os_path_exists = os.path.exists

class TestFilesHelper:
    @property
    def root_dir(self):
        return str(Path(__file__).resolve().parent.parent.parent.parent)

    def test_bad_mode(self):
        with pytest.raises(ValueError) as error:
            FilesHelper("hamburger")

        assert "not a valid mode" in str(error.value)

    def test_demo(self):
        files_helper = FilesHelper("demo")
        assert files_helper.targets_file == \
            self.root_dir + "/target_tiller/demo/files/demo_targets.yaml"
        assert files_helper.transactions_configs_file == \
            self.root_dir + "/target_tiller/demo/files/demo_transactions_configs.yaml"

        assert files_helper.portfolio_files == \
            [self.root_dir + "/target_tiller/demo/files/demo_portfolio1.yaml",
             self.root_dir + "/target_tiller/demo/files/demo_portfolio2.yaml",
             self.root_dir + "/target_tiller/demo/files/demo_portfolio3.yaml"]

    def test_env(self):
        with mock.patch.dict(os.environ,
                             {"TARGETS_FILE": "/some/dir/targets.yaml",
                              "TRANSACTIONS_CONFIGS_FILE": \
                              "/some/dir/transactions_configs.yaml",
                              "PORTFOLIO_FILES": \
                              "/some/dir/portfolio1.yaml,"\
                              "/some/dir/portfolio2.yaml"}):
            files_helper = FilesHelper("env")

            assert files_helper.targets_file == "/some/dir/targets.yaml"
            assert files_helper.transactions_configs_file == \
                "/some/dir/transactions_configs.yaml"
            assert files_helper.portfolio_files == \
                ["/some/dir/portfolio1.yaml",
                 "/some/dir/portfolio2.yaml"]

    def mock_os_path_exists(self, path):
        # Pretend the paths exist to the user files, even if they don't
        if path in [self.root_dir + "/targets.yaml",
                    self.root_dir + "/transactions_configs.yaml"]:
            return True
        return backup_os_path_exists(path)

    def test_user(self, mocker):
        # Patch os.path.exists with fake version above to find user files
        mock_exists = mocker.patch("os.path.exists")
        mock_exists.side_effect = self.mock_os_path_exists

        # Run the test that uses os.path.exists
        files_helper = FilesHelper("user")

        assert files_helper.targets_file == self.root_dir + "/targets.yaml"
        assert files_helper.transactions_configs_file == \
            self.root_dir + "/transactions_configs.yaml"

    def test_report(self, capsys):
        files_helper = FilesHelper("demo")
        files_helper.report()
        captured = capsys.readouterr()
        assert (self.root_dir + "/target_tiller/demo/files/demo_targets.yaml") in \
          captured.out
        # TODO: more tests of output
