import importlib
import pkgutil
from typing import Dict, Any

class PluginManager:
    """
    Dynamically loads agent plugins for expansion and learning.
    """
    def __init__(self, base_package: str):
        self.base_package = base_package
        self.plugins: Dict[str, Any] = {}

    def discover_plugins(self):
        package = importlib.import_module(self.base_package)
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
            if not is_pkg:
                module = importlib.import_module(f"{self.base_package}.{name}")
                self.plugins[name] = module

    def get_plugin(self, name: str):
        return self.plugins.get(name)
