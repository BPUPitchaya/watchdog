"""
Local Settings Management
Handles local application settings and preferences only - no user profiles or cloud sync
"""

import json
import os
from typing import Dict, Any


class LocalSettings:
    """Manages local application settings and preferences"""
    
    DEFAULT_SETTINGS = {
        'auto_start': True,
        'packet_limit': 0,
        'alert_threshold': 10,
        'retention_days': 30,
        'anonymize': True,
        'delete_on_exit': False,
        'enable_notifications': True,
        'sound_alerts': True,
        'system_tray': True,
        'alert_threats': True,
        'alert_anomalies': True,
        'alert_system': False,
        'onboarding_completed': False,
        'theme': 'dark',
        'language': 'en',
        'font_size': 12,
        'ml_sample_rate': 5,  # Only predict every Nth packet for performance
        'refresh_rate': 1000,
        'log_level': 'INFO'
    }
    
    def __init__(self, settings_file='local_settings.json'):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    return {**self.DEFAULT_SETTINGS, **loaded}
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.DEFAULT_SETTINGS.copy()
        return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a setting value"""
        self.settings[key] = value
        return self.save_settings()
    
    def update(self, new_settings: Dict[str, Any]) -> bool:
        """Update multiple settings"""
        self.settings.update(new_settings)
        return self.save_settings()
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.save_settings()
    
    def export_settings(self) -> str:
        """Export settings as JSON string"""
        return json.dumps(self.settings, indent=2)
    
    def import_settings(self, settings_json: str) -> bool:
        """Import settings from JSON string"""
        try:
            imported = json.loads(settings_json)
            self.settings.update(imported)
            return self.save_settings()
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False


class SettingsManager:
    """Manager for local application settings only"""
    
    def __init__(self):
        self.settings = LocalSettings()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.settings
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        return self.settings.get(key, default)
    
    def save_all(self) -> bool:
        """Save all settings"""
        return self.settings.save_settings()
    
    def update(self, new_settings: Dict[str, Any]) -> bool:
        """Update multiple settings"""
        return self.settings.update(new_settings)
    
    def is_first_time_user(self) -> bool:
        """Check if this is a first-time user"""
        return not self.settings.get('onboarding_completed', False)
    
    def mark_onboarding_complete(self) -> bool:
        """Mark onboarding as complete"""
        return self.settings.set('onboarding_completed', True)
