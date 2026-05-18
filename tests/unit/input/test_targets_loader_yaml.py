import os

from target_tiller.input import TargetsLoaderYAML


class TestTargetsLoaderYAML:
    def test_all(self):
        dir_path = os.path.dirname(__file__)
        fixtures_path = dir_path + "/../../fixtures"
        targets_loader = TargetsLoaderYAML(fixtures_path + "/fake_targets.yaml")
        targets = targets_loader.targets
        assert set(targets.symbols) == {"WTF", "LOL", "HUH"}
        assert targets.weight("WTF") == 0.4
        assert targets.weight("LOL") == 0.35
        assert targets.weight("HUH") == 0.25
