"""
Hermes APK - Lain Temali Renk Paleti ve Tema
"""
# Renk Paleti (Serial Experiments Lain dayagi)
COLORS = {
    "bg_dark":      (0.04, 0.04, 0.06, 1),    # #0a0a0f cok koyu siyah-mavi
    "bg_card":      (0.08, 0.08, 0.12, 1),     # #14141e koyu kart
    "bg_input":     (0.06, 0.06, 0.10, 1),     # #0f0f1a input arka plan
    "primary":      (0.42, 0.13, 0.66, 1),     # #6b21a8 mor (Lain tisiirtui)
    "primary_light":(0.66, 0.33, 0.97, 1),     # #a855f7 acik mor
    "secondary":    (0.05, 0.65, 0.92, 1),     # #0ea5e9 cyan/mavi
    "accent":       (0.0, 0.8, 0.6, 1),        # #00cc96 neon yesil
    "text":         (0.89, 0.91, 0.95, 1),      # #e2e8f0 acik gri
    "text_dim":     (0.39, 0.45, 0.55, 1),     # #64748b gri
    "text_muted":   (0.29, 0.33, 0.41, 1),     # #4a5568 koyu gri
    "danger":       (0.94, 0.27, 0.27, 1),     # #ef4444 kirmizi
    "success":      (0.13, 0.77, 0.37, 1),     # #22c55e yesil
    "warning":      (0.92, 0.7, 0.03, 1),      # #eab308 sari
    "border":       (0.15, 0.15, 0.22, 1),     # #262638 border
    "glow":         (0.42, 0.13, 0.66, 0.3),   # mor glow (alpha)
}

# Gradient degerler (mor -> cyan)
GRADIENT_PRIMARY = ["#6b21a8", "#7c3aed", "#0ea5e9"]
GRADIENT_DARK = ["#0a0a0f", "#14141e", "#1e1e2e"]

# Boyutlar
DIMS = {
    "padding_sm": 4,
    "padding_md": 8,
    "padding_lg": 16,
    "padding_xl": 24,
    "radius_sm": 4,
    "radius_md": 8,
    "radius_lg": 12,
    "font_xs": 10,
    "font_sm": 12,
    "font_md": 14,
    "font_lg": 18,
    "font_xl": 24,
    "font_hero": 32,
    "btn_height": 44,
    "input_height": 48,
    "card_height": 80,
    "icon_sm": 16,
    "icon_md": 24,
    "icon_lg": 32,
    "fab_size": 56,
    "nav_height": 60,
    "status_bar": 24,
}

# Animasyon sureleri (ms)
ANIM = {
    "fast": 0.1,
    "normal": 0.2,
    "slow": 0.3,
    "very_slow": 0.5,
}

# Lain "Wired" status mesajlari
LAIN_STATUS = {
    "online": "Wired",
    "offline": "Disconnected",
    "syncing": "Synchronizing...",
    "error": "Protocol Error",
    "standby": "Standby",
}

# Lain temali UI mesajlari
LAIN_MESSAGES = {
    "boot": "The Wired is everywhere...",
    "ready": "Protocol initialized.",
    "thinking": "Processing...",
    "error": "An error occurred in the Wired.",
    "goodbye": "See you in the Wired.",
    "welcome": "Welcome to Hermes.",
    "no_results": "No signals found.",
    "loading": "Connecting to the Wired...",
}
