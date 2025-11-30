"""
Configuration Manager for the application
"""
import yaml
import os


class ConfigManager:
    """Manages application configuration from YAML files"""
    
    def __init__(self, config_path=None):
        """
        Initialize the ConfigManager
        
        Args:
            config_path: Optional path to the configuration file
        """
        self.config_path = config_path
        self.config = {}
    
    def load_config(self, config_path=None):
        """
        Load configuration from a YAML file
        
        Args:
            config_path: Path to the configuration file (optional if set in __init__)
        
        Returns:
            dict: Configuration dictionary
        """
        path = config_path or self.config_path
        
        if not path or not os.path.exists(path):
            # Return default configuration if file doesn't exist
            return self._get_default_config()
        
        try:
            with open(path, 'r') as file:
                self.config = yaml.safe_load(file) or {}
                return self.config
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """
        Get default configuration values
        
        Returns:
            dict: Default configuration dictionary
        """
        return {
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
            'DEBUG': os.environ.get('DEBUG', 'True').lower() == 'true',
            'TESTING': False,
            'MAIL_SERVER': os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
            'MAIL_PORT': int(os.environ.get('MAIL_PORT', 465)),
            'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true',
            'MAIL_USE_SSL': os.environ.get('MAIL_USE_SSL', 'True').lower() == 'true',
            'MAIL_USERNAME': os.environ.get('MAIL_USERNAME', ''),
            'MAIL_PASSWORD': os.environ.get('SMTP_SECRET_KEY', ''),
            'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@matcha.com'),
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
            'UPLOAD_FOLDER': 'static/profiles',
        }
    
    def get(self, key, default=None):
        """
        Get a configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def update(self, new_config):
        """
        Update configuration with new values
        
        Args:
            new_config: Dictionary of new configuration values
        """
        self.config.update(new_config)
