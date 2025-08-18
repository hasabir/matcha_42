import os
import yaml

class ConfigManager:
    def __init__(self, config_file_path: str) -> None:
        self.config_file_path = config_file_path
        self.config = self.load_yaml(config_file_path)

    def load_yaml(self, config_file_path: str) -> dict:
        
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Configuration file not found: {config_file_path}")

        with open(config_file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data

    def _get(self, key: str):
        return self.config.get(key)

    def _set(self, key: str, value) -> None:
        self.config[key] = value
        self.save_yaml()

    def save_yaml(self) -> None:
        with open(self.config_file_path, 'w') as file:
            yaml.safe_dump(self.config, file)

    def get_metadata(self):
        return self.config
    
    def __check(self, config):
        ...
