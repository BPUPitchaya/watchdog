# Theme constants for consistent styling across the dashboard
THEMES = {
    'default': {
        'primary': '#00B4D8',
        'secondary': '#0077B6',
        'success': '#00B4D8',
        'warning': '#FF9F43',
        'danger': '#FF6B6B',
        'bg_dark': '#0A1628',
        'bg_card': '#0D1F35',
        'bg_header': '#071220',
        'text_primary': '#FFFFFF',
        'text_secondary': '#94A3B8',
        'border': '#1E3A5F',
        'border_highlight': '#00B4D8',
        'font_mono': "'Consolas', 'Source Code Pro', 'Courier New', monospace",
        'gauge_bg': '#1A3A4A',
        'gauge_active': '#00B4D8',
        'risk_low': '#00B4D8',
        'risk_high': '#FF6B6B'
    },
    'light': {
        'primary': '#0077B6',
        'secondary': '#00B4D8',
        'success': '#22C55E',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'bg_dark': '#F8FAFC',
        'bg_card': '#FFFFFF',
        'bg_header': '#F1F5F9',
        'text_primary': '#1E293B',
        'text_secondary': '#64748B',
        'border': '#E2E8F0',
        'border_highlight': '#0077B6',
        'font_mono': "'Consolas', 'Source Code Pro', 'Courier New', monospace",
        'gauge_bg': '#E2E8F0',
        'gauge_active': '#0077B6',
        'risk_low': '#22C55E',
        'risk_high': '#EF4444'
    },
    'dark': {
        'primary': '#00B4D8',
        'secondary': '#0891B2',
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'bg_dark': '#000000',
        'bg_card': '#1C1C1E',
        'bg_header': '#0A0A0A',
        'text_primary': '#FFFFFF',
        'text_secondary': '#A1A1AA',
        'border': '#3F3F46',
        'border_highlight': '#00B4D8',
        'font_mono': "'Consolas', 'Source Code Pro', 'Courier New', monospace",
        'gauge_bg': '#27272A',
        'gauge_active': '#00B4D8',
        'risk_low': '#10B981',
        'risk_high': '#EF4444'
    }
}

# Current active theme (default)
THEME = THEMES['default'].copy()

def set_theme(theme_name):
    """Switch the active theme."""
    if theme_name in THEMES:
        # Update THEME in-place so all references see the change
        THEME.clear()
        THEME.update(THEMES[theme_name])
        return True
    return False