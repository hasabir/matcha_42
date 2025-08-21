import os
import yaml

class ConfigManager:
    def __init__(self, config_file_path: str) -> None:
        self.config_file_path = config_file_path
        self.config = self.load_config(config_file_path)

    def load_config(self, config_file_path: str) -> dict:
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Configuration file not found: {config_file_path}")

        with open(config_file_path, 'r') as file:
            config = yaml.safe_load(file)
        
        def replace_env_vars(obj):
            if isinstance(obj, dict):
                return {k: replace_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_env_vars(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
                env_var = obj[2:-1]
                # Handle default values: ${VAR:-default}
                if ':-' in env_var:
                    var_name, default_value = env_var.split(':-', 1)
                    return os.environ.get(var_name, default_value)
                else:
                    return os.environ.get(env_var, obj)  # Return original if not found
            return obj
    
        return replace_env_vars(config)

    def __getitem__(self, key: str):
        return self.config.get(key)

    def __setitem__(self, key: str, value) -> None:
        self.config[key] = value
        self.save_yaml()

    def save_yaml(self) -> None:
        with open(self.config_file_path, 'w') as file:
            yaml.safe_dump(self.config, file)

    def get_metadata(self):
        return self.config
    
    def __check(self, config):
        ...
