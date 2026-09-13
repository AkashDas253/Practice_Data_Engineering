from glob import glob

from modules.base import Component


class GlobDiscovery(Component):
    stage = "discovery"
    type = "glob"

    def execute(self, data=None):
        path = self.config["path"]

        return [
            filename
            for filename in glob(path)
        ]
