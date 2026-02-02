"""
Configuration package for the webtoon generation system.

This package contains configuration classes and utilities for managing
application settings, including enhanced panel generation configuration.
"""

# Import main settings from the settings module
from .settings import Settings, get_settings, settings

# Import enhanced panel configuration
from .enhanced_panel_config import (
    EnhancedPanelConfig,
    GenreType,
    get_enhanced_panel_config,
    update_enhanced_panel_config
)

__all__ = [
    # Main settings
    "Settings",
    "get_settings", 
    "settings",
    # Enhanced panel configuration
    "EnhancedPanelConfig",
    "GenreType", 
    "get_enhanced_panel_config",
    "update_enhanced_panel_config"
]