"""Configuration management for ReconForge."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for ReconForge."""

    DEFAULT_CONFIG = {
        "timeout": 10.0,
        "port_scan_timeout": 2.0,
        "max_workers": 4,
        "concurrent_scanning": True,
        "cache_enabled": True,
        "cache_ttl": 86400,  # 24 hours
        "verbose": False,
        "retry_attempts": 3,
        "retry_delay": 1.0,
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration."""
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".reconforge" / "config.json"
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                # Merge with defaults
                config = self.DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except (json.JSONDecodeError, IOError):
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

    def reset(self) -> None:
        """Reset to default configuration."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()

    def __repr__(self) -> str:
        """String representation."""
        return f"Config({self.config_path})"


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
