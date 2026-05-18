"""This module defines the TargetsLoaderYAML class"""

import yaml

from ..targets import Targets


class TargetsLoaderYAML:
    """Read in some rebalancing targets from a YAML file."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self._config = None
        self._targets = None

    @property
    def config(self) -> dict:
        """The parsed parts of the YAML file."""
        if not self._config:
            with open(self.filename, encoding="utf-8") as file:
                self._config = yaml.load(file, Loader=yaml.SafeLoader)

        return self._config

    @property
    def targets(self) -> Targets:
        """The targets loaded from disk."""
        if not self._targets:
            dict_targets = {d["symbol"] : d["weight"]
                            for d in self.config["targets"] }
            self._targets = Targets(dict_targets)
        return self._targets
