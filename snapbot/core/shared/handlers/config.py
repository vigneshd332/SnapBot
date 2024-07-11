from typing import Any, Dict
import toml


class ConfigLoader:
    def __init__(self) -> None:
        self.path = "snapbot/data/config.toml"

    def load(self) -> Dict[str, Any]:
        """Returns the configuration data from the config file."""
        with open(self.path, "r") as file:
            return toml.load(file)

    def save(self, data: Dict[str, Any]) -> None:
        """Dumps the specified `data` to the config file."""
        with open(self.path, "w") as file:
            toml.dump(data, file)
