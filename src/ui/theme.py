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
        'text_primary': '#E0E0E0',
        'text_secondary': '#8A94A6',
        'border': '#1E3A5F',
        'border_highlight': '#00B4D8',
        'table_header_bg': '#0D1F35',
        'table_row_even': '#131C26',
        'table_row_odd': '#0F161E',
        'input_bg': '#0D131A',
        'chat_user_bg': '#1A3A4A',
        'chat_ai_bg': '#0D1F35',
        'font_mono': "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
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
        'bg_dark': '#E8F0F7',
        'bg_card': '#FFFFFF',
        'bg_header': '#1A365D',
        'text_primary': '#1A365D',
        'text_secondary': '#4A5568',
        'border': '#CBD5E0',
        'border_highlight': '#0077B6',
        'font_mono': "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
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
        'font_mono': "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
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