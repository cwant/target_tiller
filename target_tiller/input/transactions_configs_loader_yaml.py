"""This module defines the TransactionsConfig class"""

import yaml

from ..transactions_config import TransactionsConfig


class TransactionsConfigsLoaderYAML:
    """A class for loading a TransactionsConfig YAML file"""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self._config = None
        self._transactions_configs = None

    @property
    def config(self) -> list:
        """Load from the file and store."""
        if not self._config:
            with open(self.filename, encoding="utf-8") as file:
                self._config = yaml.load(file, Loader=yaml.SafeLoader)

        return self._config

    @property
    def transactions_configs(self) -> list:
        """Return the loaded TransactionsConfig objects."""
        if not self._transactions_configs:
            self._transactions_configs = []
            for transactions_config_hash in self.config:
                self._transactions_configs += \
                    [TransactionsConfig(**transactions_config_hash)]

        return self._transactions_configs
