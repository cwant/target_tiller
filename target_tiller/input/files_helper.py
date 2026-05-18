"""This module defines the FilesHelper class"""

import os
from pathlib import Path

from dotenv import load_dotenv


class FilesHelper:
    """Objects of this class easily provide files for the TargetTiller pipeline.

    Objects of this class specifically provide three things, via properties:

    * self.targets_file: this is a path/filename to a targets_file (YAML)
    * self.transactions_configs_file: this is a path/filename to a
      transactions_configs file (YAML)
    * self.portfolio_files: this is a list of paths/filenames to some
      portfolio files (CSV)

    The object can find files in five ways:

    * The object can be initialized with a 'mode' parameter. Values are
      'demo', 'env', and 'user', and these override any other ways
      for choosing which files to use.
    * it can use some demo files provided with the software (default).
    * if can look in the either the current directory, or if not found
      there in the root directory of this repository to find
      targets.yaml and transactions_configs.yaml (not supplied). If either
      (or both) files are found, it will use these instead of the demo files.
    * it can look at some environment files to find the files:

      * TARGETS_FILE
      * TRANSACTIONS_CONFIGS_FILE
      * PORTFOLIO_FILES

      The last environment variable is a comma separted list of files to use.
      If any of these environment variables are set, they override any of the
      other methods for finding files.
      Note that there is no standard place to put portfolio files, so if you
      want to override the demo values, you need to use environment variables.

    * There is one other way to influence what files you recieve from this
      type of object: the environment varialbes FORCE_DEMO_FILES and
      FORCE_ENV_FILES will try to force the demo to use those files
      instead of what would ordinarily be selected. This is particularly
      useful if you are using dotenv-python to configure these options.
    """

    # Public methods / properties
    def __init__(self, mode: str | None = None) -> None:
        """Create new instance. Uses config from the class, files from
        standard locations, and values loaded from the environment.
        The files used can be set by the mode parameter, or via other
        methods to autodetect (env vars, standard locations).
        """
        load_dotenv()
        self._targets_file = None
        self._transactions_configs_file = None
        self._portfolio_files = None
        if mode not in ["user", "env", "demo", None]:
            raise ValueError(f"{mode} is not a valid mode")
        self._mode = mode

    @property
    def targets_file(self) -> str:
        """The (calculated) location of the targets file (YAML)"""
        if not self._targets_file:
            self._targets_file = self.__get_filenames("targets_file")[0]

        return self._targets_file

    @property
    def transactions_configs_file(self) -> str:
        """The (calculated) location of the transactions configs file (YAML)"""
        if not self._transactions_configs_file:
            self._transactions_configs_file = \
                self.__get_filenames("transactions_configs_file")[0]

        return self._transactions_configs_file

    @property
    def portfolio_files(self) -> list:
        """The (calculated) locations of the portfolio files (CSV)."""
        if not self._portfolio_files:
            self._portfolio_files = self.__get_filenames("portfolio_files")

        return self._portfolio_files

    def report(self) -> None:
        """A simple text report of the file locations and their contents."""
        self.__report_targets_file()
        self.__report_transactions_configs_file()
        self.__report_portfolio_files()

    # Private methods
    def __config(self, mode: str) -> dict | None:
        return {
            "targets_file": {
                "env": "TARGETS_FILE",
                "user": "targets.yaml",
                "demo": "demo_targets.yaml"
            },
            "portfolio_files": {
                "env": "PORTFOLIO_FILES",
                "demo": [
                    "demo_portfolio1.yaml",
                    "demo_portfolio2.yaml",
                    "demo_portfolio3.yaml"
                ]
                # TODO: Maybe list user defaults as a directory?
            },
            "transactions_configs_file": {
                "env": "TRANSACTIONS_CONFIGS_FILE",
                "user": "transactions_configs.yaml",
                "demo": "demo_transactions_configs.yaml"
            }
        }.get(mode)

    def __get_filenames(self, file_type: str) -> list:
        # Always returns a list, even if there is only one file

        config = self.__config(file_type)

        files = None
        match self._mode:
            case "env":
                files = self.__get_env_files(config)
            case "user":
                files = self.__get_user_files(config)
            case "demo":
                files = self.__get_demo_files(config)

        if files:
            return files

        if not os.environ.get("FORCE_DEMO_FILES") and \
           not os.environ.get("FORCE_USER_FILES"):
            files = self.__get_env_files(config)
            if files:
                return files

        if not os.environ.get("FORCE_DEMO_FILES"):
            files = self.__get_user_files(config)
            if files:
                return files

        return self.__get_demo_files(config)

    def __get_env_files(self, config: dict) -> list:
        # This will either be single file, of comma separated set of files
        env_file = os.environ.get(config.get("env"))
        if env_file:
            env_file = env_file.split(",")
            env_file = [x.strip() for x in env_file]
            return [self.__resolve_path(x) for x in env_file]

        return None

    def __get_user_files(self, config: dict) -> list:
        # This will always be a single file
        this_file = config.get("user")
        if this_file:
            user_file = self.__resolve_path(this_file,
                                            path_type="current_dir")
            if os.path.exists(user_file):
                return [user_file]
            user_file = self.__resolve_path(this_file,
                                            path_type="code_dir")
            if os.path.exists(user_file):
                return [user_file]

        return None

    def __get_demo_files(self, config: dict) -> list:
        # This will either be a list, single file, or multiple files
        demo_file = config.get("demo")
        if not isinstance(demo_file, list):
            demo_file = demo_file.split(",")
            demo_file = [x.strip() for x in demo_file]
        return [self.__resolve_path(x, path_type="demo_dir") for x in demo_file]

    def __resolve_path(self, filename: str, path_type: str = "current_dir") -> str:
        if filename[0] == "/":
            file_path = filename
        else:
            # Resolve relative path
            this_dir = None
            if path_type == "current_dir":
                this_dir = "."
            elif path_type == "code_dir":
                this_dir = Path(__file__).resolve().parent.parent.parent
            elif path_type == "demo_dir":
                this_dir = Path(__file__).resolve().parent.parent
                filename = f"demo/files/{filename}"
            file_path = f"{this_dir}/{filename}"
        return str(Path(file_path).resolve())

    def __report_file(self, filename: str, title: str | None = None) -> None:
        # TODO: make this pretty? Maybe HTML reporter class
        if title:
            print(title)
        print(filename)
        with open(filename, encoding="utf-8") as f:
            print(f.read())

    def __report_targets_file(self) -> None:
        self.__report_file(self.targets_file, title="Targets file")

    def __report_portfolio_files(self) -> None:
        print("Portfolio Files")

        for file in self.portfolio_files:
            self.__report_file(file)
            print()

    def __report_transactions_configs_file(self) -> None:
        self.__report_file(self.transactions_configs_file,
                           "Transactions Configs file")
