"""
Atlas UI Design System
Professional, Claude-inspired styling for Streamlit applications.
"""

import streamlit as st


# ─── Design Tokens ────────────────────────────────────────────────────────

# Color palette - professional neutrals with a refined accent
COLORS = {
    # Neutrals (light mode)
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F7F7F8",
    "bg_tertiary": "#EEEEEF",
    "bg_card": "#FFFFFF",
    "bg_card_hover": "#FAFAFA",
    "border_subtle": "#E5E5E6",
    "border_default": "#D4D4D8",
    "border_strong": "#A3A3AA",
    "text_primary": "#1A1A1A",
    "text_secondary": "#52525B",
    "text_muted": "#A1A1AA",
    "text_inverse": "#FFFFFF",

    # Accent - refined amber/orange (professional, not aggressive)
    "accent": "#C4772C",
    "accent_hover": "#B06828",
    "accent_light": "#FEF3E2",
    "accent_border": "#F5D9B8",

    # Semantic colors
    "success": "#15803D",
    "success_bg": "#F0FDF4",
    "success_border": "#BBF7D0",
    "warning": "#B45309",
    "warning_bg": "#FFF7ED",
    "warning_border": "#FDE68A",
    "error": "#B91C1C",
    "error_bg": "#FEF2F2",
    "error_border": "#FECACA",
    "info": "#1D4ED8",
    "info_bg": "#EFF6FF",
    "info_border": "#BFDBFE",

    # Dark mode (auto-applied via media query)
    "dark_bg_primary": "#0C0C0C",
    "dark_bg_secondary": "#141414",
    "dark_bg_tertiary": "#1C1C1C",
    "dark_bg_card": "#181818",
    "dark_bg_card_hover": "#1F1F1F",
    "dark_border_subtle": "#2A2A2A",
    "dark_border_default": "#3A3A3A",
    "dark_border_strong": "#4A4A4A",
    "dark_text_primary": "#FAFAFA",
    "dark_text_secondary": "#A1A1AA",
    "dark_text_muted": "#71717A",
    "dark_accent": "#D9A34E",
    "dark_accent_hover": "#E8B460",
    "dark_accent_light": "#2D2418",
    "dark_accent_border": "#4A3A1E",
}

# Spacing scale (based on 4px unit)
SPACE = {
    "0": "0",
    "1": "0.25rem",   # 4px
    "2": "0.5rem",    # 8px
    "3": "0.75rem",   # 12px
    "4": "1rem",      # 16px
    "5": "1.25rem",   # 20px
    "6": "1.5rem",    # 24px
    "8": "2rem",      # 32px
    "10": "2.5rem",   # 40px
    "12": "3rem",     # 48px
    "16": "4rem",     # 64px
    "20": "5rem",     # 80px
}

# Typography
TYPOGRAPHY = {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "font_mono": "'JetBrains Mono', 'Fira Code', 'SF Mono', monospace",
    "size_xs": "0.75rem",    # 12px
    "size_sm": "0.875rem",   # 14px
    "size_base": "1rem",     # 16px
    "size_lg": "1.125rem",   # 18px
    "size_xl": "1.25rem",    # 20px
    "size_2xl": "1.5rem",    # 24px
    "size_3xl": "1.875rem",  # 30px
    "size_4xl": "2.25rem",   # 36px
    "size_5xl": "3rem",      # 48px
    "weight_normal": "400",
    "weight_medium": "500",
    "weight_semibold": "600",
    "weight_bold": "700",
    "line_tight": "1.1",
    "line_snug": "1.375",
    "line_normal": "1.5",
    "line_relaxed": "1.625",
}

# Border radius
RADIUS = {
    "none": "0",
    "sm": "0.25rem",    # 4px
    "md": "0.375rem",   # 6px
    "lg": "0.5rem",     # 8px
    "xl": "0.75rem",    # 12px
    "2xl": "1rem",      # 16px
    "full": "9999px",
}

# Shadows
SHADOWS = {
    "none": "none",
    "xs": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    "sm": "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
    "md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
    "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
    "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
    "inner": "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)",
}

# Transitions
TRANSITIONS = {
    "fast": "150ms cubic-bezier(0.4, 0, 0.2, 1)",
    "normal": "200ms cubic-bezier(0.4, 0, 0.2, 1)",
    "slow": "300ms cubic-bezier(0.4, 0, 0.2, 1)",
}

# Breakpoints
BREAKPOINTS = {
    "sm": "640px",
    "md": "768px",
    "lg": "1024px",
    "xl": "1280px",
    "2xl": "1536px",
}


# ─── CSS Generation ──────────────────────────────────────────────────────

def generate_css() -> str:
    """Generate the complete CSS for the design system."""
    return f"""
<style>
/* ============================================================
   Atlas Design System - Professional UI Framework
   Inspired by Claude's clean, minimal aesthetic
   ============================================================ */

/* ─── CSS Custom Properties ──────────────────────────────── */
:root {{
    /* Light mode (default) */
    --color-bg-primary: {COLORS['bg_primary']};
    --color-bg-secondary: {COLORS['bg_secondary']};
    --color-bg-tertiary: {COLORS['bg_tertiary']};
    --color-bg-card: {COLORS['bg_card']};
    --color-bg-card-hover: {COLORS['bg_card_hover']};
    --color-border-subtle: {COLORS['border_subtle']};
    --color-border-default: {COLORS['border_default']};
    --color-border-strong: {COLORS['border_strong']};
    --color-text-primary: {COLORS['text_primary']};
    --color-text-secondary: {COLORS['text_secondary']};
    --color-text-muted: {COLORS['text_muted']};
    --color-text-inverse: {COLORS['text_inverse']};
    --color-accent: {COLORS['accent']};
    --color-accent-hover: {COLORS['accent_hover']};
    --color-accent-light: {COLORS['accent_light']};
    --color-accent-border: {COLORS['accent_border']};
    --color-success: {COLORS['success']};
    --color-success-bg: {COLORS['success_bg']};
    --color-success-border: {COLORS['success_border']};
    --color-warning: {COLORS['warning']};
    --color-warning-bg: {COLORS['warning_bg']};
    --color-warning-border: {COLORS['warning_border']};
    --color-error: {COLORS['error']};
    --color-error-bg: {COLORS['error_bg']};
    --color-error-border: {COLORS['error_border']};
    --color-info: {COLORS['info']};
    --color-info-bg: {COLORS['info_bg']};
    --color-info-border: {COLORS['info_border']};

    --font-family: {TYPOGRAPHY['font_family']};
    --font-mono: {TYPOGRAPHY['font_mono']};
    --radius-sm: {RADIUS['sm']};
    --radius-md: {RADIUS['md']};
    --radius-lg: {RADIUS['lg']};
    --radius-xl: {RADIUS['xl']};
    --radius-2xl: {RADIUS['2xl']};
    --radius-full: {RADIUS['full']};
    --shadow-xs: {SHADOWS['xs']};
    --shadow-sm: {SHADOWS['sm']};
    --shadow-md: {SHADOWS['md']};
    --shadow-lg: {SHADOWS['lg']};
    --shadow-xl: {SHADOWS['xl']};
    --transition-fast: {TRANSITIONS['fast']};
    --transition-normal: {TRANSITIONS['normal']};
    --transition-slow: {TRANSITIONS['slow']};
}}

/* Dark mode */
@media (prefers-color-scheme: dark) {{
    :root {{
        --color-bg-primary: {COLORS['dark_bg_primary']};
        --color-bg-secondary: {COLORS['dark_bg_secondary']};
        --color-bg-tertiary: {COLORS['dark_bg_tertiary']};
        --color-bg-card: {COLORS['dark_bg_card']};
        --color-bg-card-hover: {COLORS['dark_bg_card_hover']};
        --color-border-subtle: {COLORS['dark_border_subtle']};
        --color-border-default: {COLORS['dark_border_default']};
        --color-border-strong: {COLORS['dark_border_strong']};
        --color-text-primary: {COLORS['dark_text_primary']};
        --color-text-secondary: {COLORS['dark_text_secondary']};
        --color-text-muted: {COLORS['dark_text_muted']};
        --color-accent: {COLORS['dark_accent']};
        --color-accent-hover: {COLORS['dark_accent_hover']};
        --color-accent-light: {COLORS['dark_accent_light']};
        --color-accent-border: {COLORS['dark_accent_border']};
    }}
}}

/* Force dark mode when Streamlit theme is dark */
[data-theme="dark"] {{
    --color-bg-primary: {COLORS['dark_bg_primary']} !important;
    --color-bg-secondary: {COLORS['dark_bg_secondary']} !important;
    --color-bg-tertiary: {COLORS['dark_bg_tertiary']} !important;
    --color-bg-card: {COLORS['dark_bg_card']} !important;
    --color-bg-card-hover: {COLORS['dark_bg_card_hover']} !important;
    --color-border-subtle: {COLORS['dark_border_subtle']} !important;
    --color-border-default: {COLORS['dark_border_default']} !important;
    --color-border-strong: {COLORS['dark_border_strong']} !important;
    --color-text-primary: {COLORS['dark_text_primary']} !important;
    --color-text-secondary: {COLORS['dark_text_secondary']} !important;
    --color-text-muted: {COLORS['dark_text_muted']} !important;
    --color-accent: {COLORS['dark_accent']} !important;
    --color-accent-hover: {COLORS['dark_accent_hover']} !important;
    --color-accent-light: {COLORS['dark_accent_light']} !important;
    --color-accent-border: {COLORS['dark_accent_border']} !important;
}}

/* ─── Global Reset & Base ────────────────────────────────── */
#MainMenu, footer, header {{ visibility: hidden; }}

html {{
    scroll-behavior: smooth;
}}

.block-container {{
    padding-top: {SPACE['6']} !important;
    padding-bottom: {SPACE['10']} !important;
    max-width: 1200px !important;
    font-family: var(--font-family);
    color: var(--color-text-primary);
    background-color: var(--color-bg-primary);
}}

/* Smooth animations */
* {{
    transition: background-color var(--transition-fast),
                border-color var(--transition-fast),
                color var(--transition-fast),
                box-shadow var(--transition-fast),
                transform var(--transition-fast);
}}

/* ─── Typography ─────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-family);
    font-weight: {TYPOGRAPHY['weight_bold']};
    line-height: var(--line-tight);
    color: var(--color-text-primary);
    letter-spacing: -0.02em;
}}

h1 {{ font-size: {TYPOGRAPHY['size_4xl']}; margin-bottom: {SPACE['4']}; }}
h2 {{ font-size: {TYPOGRAPHY['size_3xl']}; margin-top: {SPACE['10']}; margin-bottom: {SPACE['4']}; }}
h3 {{ font-size: {TYPOGRAPHY['size_2xl']}; margin-top: {SPACE['8']}; margin-bottom: {SPACE['3']}; }}
h4 {{ font-size: {TYPOGRAPHY['size_xl']}; margin-top: {SPACE['6']}; margin-bottom: {SPACE['3']}; }}

p {{
    font-size: {TYPOGRAPHY['size_base']};
    line-height: var(--line-normal);
    color: var(--color-text-secondary);
    margin-bottom: {SPACE['4']};
}}

a {{
    color: var(--color-accent);
    text-decoration: none;
    font-weight: {TYPOGRAPHY['weight_medium']};
    transition: color var(--transition-fast);
}}
a:hover {{ color: var(--color-accent-hover); text-decoration: underline; }}

code {{
    font-family: var(--font-mono);
    font-size: 0.9em;
    background-color: var(--color-bg-tertiary);
    padding: 0.125em 0.375em;
    border-radius: var(--radius-sm);
    color: var(--color-accent);
}}

pre {{
    font-family: var(--font-mono);
    font-size: {TYPOGRAPHY['size_sm']};
    line-height: var(--line-normal);
    background-color: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-lg);
    padding: {SPACE['4']};
    overflow-x: auto;
    color: var(--color-text-primary);
}}

kbd {{
    font-family: var(--font-mono);
    font-size: {TYPOGRAPHY['size_xs']};
    background-color: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-sm);
    padding: 0.125rem 0.375rem;
    box-shadow: 0 1px 0 var(--color-border-subtle);
}}

/* ─── Layout Utilities ───────────────────────────────────── */
.section {{ margin-bottom: {SPACE['10']}; }}
.divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--color-border-default), transparent);
    margin: {SPACE['8']} 0;
    border: none;
}}

/* ─── Cards ──────────────────────────────────────────────── */
.card {{
    background-color: var(--color-bg-card);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-xl);
    padding: {SPACE['6']};
    transition: all var(--transition-normal);
}}
.card:hover {{
    border-color: var(--color-border-default);
    box-shadow: var(--shadow-lg);
    background-color: var(--color-bg-card-hover);
}}
.card-interactive {{
    cursor: pointer;
}}
.card-interactive:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
    border-color: var(--color-accent-border);
}}

.card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: {SPACE['4']};
    padding-bottom: {SPACE['3']};
    border-bottom: 1px solid var(--color-border-subtle);
}}

.card-title {{
    font-size: {TYPOGRAPHY['size_lg']};
    font-weight: {TYPOGRAPHY['weight_semibold']};
    color: var(--color-text-primary);
    margin: 0;
}}

.card-subtitle {{
    font-size: {TYPOGRAPHY['size_sm']};
    color: var(--color-text-muted);
    margin: 0;
}}

/* ─── Buttons ────────────────────────────────────────────── */
.stButton > button {{
    font-family: var(--font-family) !important;
    font-size: {TYPOGRAPHY['size_sm']} !important;
    font-weight: {TYPOGRAPHY['weight_medium']} !important;
    border-radius: var(--radius-lg) !important;
    padding: {SPACE['2']} {SPACE['5']} !important;
    border: 1px solid transparent !important;
    transition: all var(--transition-fast) !important;
    cursor: pointer !important;
    white-space: nowrap;
}}

/* Primary button */
.stButton > button[kind="primary"] {{
    background-color: var(--color-accent) !important;
    color: var(--color-text-inverse) !important;
    border-color: var(--color-accent) !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: var(--color-accent-hover) !important;
    border-color: var(--color-accent-hover) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button[kind="primary"]:active {{
    transform: translateY(0) !important;
    box-shadow: var(--shadow-xs) !important;
}}

/* Secondary button */
.stButton > button[kind="secondary"] {{
    background-color: var(--color-bg-card) !important;
    color: var(--color-text-primary) !important;
    border-color: var(--color-border-default) !important;
}}
.stButton > button[kind="secondary"]:hover {{
    background-color: var(--color-bg-card-hover) !important;
    border-color: var(--color-border-strong) !important;
    box-shadow: var(--shadow-sm) !important;
}}

/* Tertiary/ghost button */
.stButton > button[kind="tertiary"] {{
    background-color: transparent !important;
    color: var(--color-text-secondary) !important;
    border-color: transparent !important;
}}
.stButton > button[kind="tertiary"]:hover {{
    background-color: var(--color-bg-tertiary) !important;
    color: var(--color-text-primary) !important;
}}

/* Button widths */
.stButton > button[width="stretch"] {{ width: 100% !important; }}

/* Disabled state */
.stButton > button:disabled {{
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
}}

/* ─── Form Inputs ────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {{
    font-family: var(--font-family) !important;
    font-size: {TYPOGRAPHY['size_sm']} !important;
    background-color: var(--color-bg-card) !important;
    border: 1px solid var(--color-border-default) !important;
    border-radius: var(--radius-lg) !important;
    color: var(--color-text-primary) !important;
    padding: {SPACE['2']} {SPACE['3']} !important;
    transition: all var(--transition-fast) !important;
    width: 100% !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus {{
    border-color: var(--color-accent) !important;
    box-shadow: 0 0 0 3px var(--color-accent-light) !important;
    outline: none !important;
}}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {{
    color: var(--color-text-muted) !important;
}}

/* Labels */
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stNumberInput label,
.stSlider label,
.stCheckbox label {{
    font-size: {TYPOGRAPHY['size_sm']} !important;
    font-weight: {TYPOGRAPHY['weight_medium']} !important;
    color: var(--color-text-secondary) !important;
    margin-bottom: {SPACE['1']} !important;
}}

/* Selectbox dropdown */
.stSelectbox > div > div > div[data-baseweb="select"] > div {{
    background-color: var(--color-bg-card) !important;
    border-color: var(--color-border-default) !important;
}}

/* Slider */
.stSlider > div > div > div > div {{
    background-color: var(--color-accent) !important;
}}
.stSlider > div > div > div > div[data-baseweb="slider"] {{
    background-color: var(--color-bg-tertiary) !important;
}}

/* Checkbox */
.stCheckbox > label > div:first-child {{
    background-color: var(--color-bg-card) !important;
    border-color: var(--color-border-default) !important;
    border-radius: var(--radius-sm) !important;
}}
.stCheckbox > label > div:first-child[data-checked="true"] {{
    background-color: var(--color-accent) !important;
    border-color: var(--color-accent) !important;
}}

/* ─── Tabs ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    gap: {SPACE['2']} !important;
    background-color: transparent !important;
    padding: {SPACE['1']} !important;
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--color-border-subtle) !important;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: var(--font-family) !important;
    font-size: {TYPOGRAPHY['size_sm']} !important;
    font-weight: {TYPOGRAPHY['weight_medium']} !important;
    background-color: transparent !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: {SPACE['2']} {SPACE['4']} !important;
    color: var(--color-text-secondary) !important;
    transition: all var(--transition-fast) !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background-color: var(--color-bg-tertiary) !important;
    color: var(--color-text-primary) !important;
}}
.stTabs [aria-selected="true"] {{
    background-color: var(--color-accent) !important;
    color: var(--color-text-inverse) !important;
    box-shadow: var(--shadow-sm) !important;
}}

/* ─── Metrics ────────────────────────────────────────────── */
.stMetric {{
    background-color: var(--color-bg-card) !important;
    border: 1px solid var(--color-border-subtle) !important;
    border-radius: var(--radius-xl) !important;
    padding: {SPACE['4']} !important;
    transition: all var(--transition-normal) !important;
}}
.stMetric:hover {{
    border-color: var(--color-border-default) !important;
    box-shadow: var(--shadow-md) !important;
}}
.stMetric label {{
    font-size: {TYPOGRAPHY['size_sm']} !important;
    font-weight: {TYPOGRAPHY['weight_medium']} !important;
    color: var(--color-text-secondary) !important;
}}
.stMetric div[data-testid="stMetricValue"] {{
    font-size: {TYPOGRAPHY['size_2xl']} !important;
    font-weight: {TYPOGRAPHY['weight_bold']} !important;
    color: var(--color-text-primary) !important;
    font-family: var(--font-mono) !important;
}}
.stMetric div[data-testid="stMetricDelta"] {{
    font-size: {TYPOGRAPHY['size_sm']} !important;
    font-weight: {TYPOGRAPHY['weight_medium']} !important;
}}

/* ─── DataFrame / Tables ─────────────────────────────────── */
.stDataFrame {{
    border: 1px solid var(--color-border-subtle) !important;
    border-radius: var(--radius-xl) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stDataFrame [data-testid="stTable"] {{
    background-color: var(--color-bg-card) !important;
}}
.stDataFrame th {{
    background-color: var(--color-bg-secondary) !important;
    font-weight: {TYPOGRAPHY['weight_semibold']} !important;
    font-size: {TYPOGRAPHY['size_sm']} !important;
    color: var(--color-text-secondary) !important;
    border-bottom: 1px solid var(--color-border-default) !important;
    padding: {SPACE['3']} {SPACE['4']} !important;
}}
.stDataFrame td {{
    font-size: {TYPOGRAPHY['size_sm']} !important;
    color: var(--color-text-primary) !important;
    border-bottom: 1px solid var(--color-border-subtle) !important;
    padding: {SPACE['3']} {SPACE['4']} !important;
}}
.stDataFrame tr:hover td {{
    background-color: var(--color-bg-secondary) !important;
}}

/* ─── Expander ───────────────────────────────────────────── */
.streamlit-expanderHeader {{
    font-family: var(--font-family) !important;
    font-size: {TYPOGRAPHY['size_base']} !important;
    font-weight: {TYPOGRAPHY['weight_semibold']} !important;
    background-color: var(--color-bg-card) !important;
    border: 1px solid var(--color-border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    padding: {SPACE['3']} {SPACE['4']} !important;
    color: var(--color-text-primary) !important;
    transition: all var(--transition-fast) !important;
}}
.streamlit-expanderHeader:hover {{
    border-color: var(--color-border-default) !important;
    background-color: var(--color-bg-card-hover) !important;
}}
.streamlit-expanderContent {{
    border: 1px solid var(--color-border-subtle) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg) !important;
    padding: {SPACE['4']} !important;
    background-color: var(--color-bg-card) !important;
}}

/* ─── Sidebar ────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background-color: var(--color-bg-secondary) !important;
    border-right: 1px solid var(--color-border-subtle) !important;
}}
[data-testid="stSidebar"] .block-container {{
    padding-top: {SPACE['6']} !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: var(--color-text-primary) !important;
}}
[data-testid="stSidebar"] .stPageLink > a {{
    font-family: var(--font-family) !important;
    font-size: {TYPOGRAPHY['size_sm']} !important;
    font-weight: {TYPOGRAPHY['weight_medium']} !important;
    color: var(--color-text-secondary) !important;
    background-color: transparent !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: {SPACE['2']} {SPACE['3']} !important;
    margin: {SPACE['1']} 0 !important;
    transition: all var(--transition-fast) !important;
}}
[data-testid="stSidebar"] .stPageLink > a:hover {{
    background-color: var(--color-bg-tertiary) !important;
    color: var(--color-text-primary) !important;
    text-decoration: none !important;
}}
[data-testid="stSidebar"] .stPageLink > a[aria-current="page"] {{
    background-color: var(--color-accent-light) !important;
    color: var(--color-accent) !important;
    border-left: 3px solid var(--color-accent) !important;
}}

/* ─── Chat Messages ──────────────────────────────────────── */
.stChatMessage {{
    background-color: var(--color-bg-card) !important;
    border: 1px solid var(--color-border-subtle) !important;
    border-radius: var(--radius-xl) !important;
    padding: {SPACE['4']} !important;
    margin-bottom: {SPACE['3']} !important;
    box-shadow: var(--shadow-xs) !important;
}}
.stChatMessage [data-testid="chatAvatarIcon"] {{
    background-color: var(--color-accent-light) !important;
    color: var(--color-accent) !important;
}}

/* ─── Alerts / Status ────────────────────────────────────── */
.stAlert {{
    border-radius: var(--radius-lg) !important;
    border: 1px solid !important;
    padding: {SPACE['4']} {SPACE['5']} !important;
    font-size: {TYPOGRAPHY['size_sm']} !important;
}}
.stAlert.success {{
    background-color: var(--color-success-bg) !important;
    border-color: var(--color-success-border) !important;
    color: var(--color-success) !important;
}}
.stAlert.warning {{
    background-color: var(--color-warning-bg) !important;
    border-color: var(--color-warning-border) !important;
    color: var(--color-warning) !important;
}}
.stAlert.error {{
    background-color: var(--color-error-bg) !important;
    border-color: var(--color-error-border) !important;
    color: var(--color-error) !important;
}}
.stAlert.info {{
    background-color: var(--color-info-bg) !important;
    border-color: var(--color-info-border) !important;
    color: var(--color-info) !important;
}}

/* ─── Progress Bar ───────────────────────────────────────── */
.stProgress > div > div > div > div {{
    background-color: var(--color-accent) !important;
    border-radius: var(--radius-full) !important;
}}
.stProgress > div > div > div {{
    background-color: var(--color-bg-tertiary) !important;
    border-radius: var(--radius-full) !important;
    height: 6px !important;
}}

/* ─── Spinner ────────────────────────────────────────────── */
.stSpinner > div {{
    border-top-color: var(--color-accent) !important;
}}

/* ─── File Uploader ──────────────────────────────────────── */
.stFileUploader > div > div {{
    background-color: var(--color-bg-card) !important;
    border: 2px dashed var(--color-border-default) !important;
    border-radius: var(--radius-xl) !important;
    padding: {SPACE['8']} !important;
}}
.stFileUploader > div > div:hover {{
    border-color: var(--color-accent) !important;
    background-color: var(--color-accent-light) !important;
}}

/* ─── Tooltip ────────────────────────────────────────────── */
[data-tooltip] {{
    position: relative;
}}
[data-tooltip]::after {{
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    padding: {SPACE['1']} {SPACE['2']};
    font-size: {TYPOGRAPHY['size_xs']};
    font-weight: {TYPOGRAPHY['weight_medium']};
    background-color: var(--color-text-primary);
    color: var(--color-text-inverse);
    border-radius: var(--radius-md);
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity var(--transition-fast);
    z-index: 1000;
    margin-bottom: {SPACE['1']};
}}
[data-tooltip]:hover::after {{
    opacity: 1;
}}

/* ─── Animations ─────────────────────────────────────────── */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes slideIn {{
    from {{ opacity: 0; transform: translateX(-10px); }}
    to {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.6; }}
}}
@keyframes spin {{
    to {{ transform: rotate(360deg); }}
}}

.animate-fade-in {{ animation: fadeIn var(--transition-slow) ease-out; }}
.animate-slide-in {{ animation: slideIn var(--transition-normal) ease-out; }}
.animate-pulse {{ animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }}

/* ─── Scrollbar ──────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: var(--color-bg-secondary); }}
::-webkit-scrollbar-thumb {{ background: var(--color-border-default); border-radius: var(--radius-full); }}
::-webkit-scrollbar-thumb:hover {{ background: var(--color-border-strong); }}

/* ─── Focus Visible ──────────────────────────────────────── */
:focus-visible {{
    outline: 2px solid var(--color-accent) !important;
    outline-offset: 2px !important;
}}

/* ─── Reduced Motion ─────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }}
}}

/* ─── Print Styles ───────────────────────────────────────── */
@media print {{
    .stButton, .stTextInput, .stSelectbox, .stSlider,
    [data-testid="stSidebar"], header, footer {{
        display: none !important;
    }}
    .block-container {{ max-width: 100% !important; padding: 0 !important; }}
    .card {{ box-shadow: none !important; border: 1px solid #ccc !important; break-inside: avoid; }}
}}
</style>
"""


# ─── Helper Functions ────────────────────────────────────────────────────

def apply_design_system():
    """Apply the design system CSS to the current Streamlit page."""
    st.markdown(generate_css(), unsafe_allow_html=True)
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        button[title="Close sidebar"],
        button[aria-label="Close sidebar"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] > div:first-child > button {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)


def page_config(title: str, icon: str = "⚡", layout: str = "wide", sidebar: str = "expanded"):
    """Standardized page config with consistent settings."""
    st.set_page_config(
        page_title=f"{title} — Atlas",
        page_icon=icon,
        layout=layout,
        initial_sidebar_state=sidebar,
    )


def hero(title: str, subtitle: str = "", icon: str = ""):
    """Render a professional hero section."""
    icon_html = f'<span style="font-size: 1.2em; margin-right: {SPACE["3"]};">{icon}</span>' if icon else ""
    st.markdown(f"""
    <div class="animate-fade-in" style="text-align: center; padding: {SPACE['8']} 0 {SPACE['6']} 0;">
        <h1 style="font-size: {TYPOGRAPHY['size_5xl']}; margin-bottom: {SPACE['3']};
                   background: linear-gradient(135deg, var(--color-text-primary) 0%, var(--color-text-secondary) 100%);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            {icon_html}{title}
        </h1>
        {f'<p style="font-size: {TYPOGRAPHY["size_xl"]}; color: var(--color-text-secondary); max-width: 700px; margin: 0 auto; line-height: var(--line-relaxed);">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, description: str = "", action=None):
    """Render a consistent section header."""
    action_html = f'<div>{action}</div>' if action else ""
    st.markdown(f"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between;
                gap: {SPACE['4']}; margin-bottom: {SPACE['6']}; flex-wrap: wrap;">
        <div>
            <h2 style="margin: 0 0 {SPACE['1']} 0;">{title}</h2>
            {f'<p style="margin: 0; color: var(--color-text-secondary);">{description}</p>' if description else ''}
        </div>
        {action_html}
    </div>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, delta: str = "", delta_color: str = "normal"):
    """Render a styled metric card (for use in custom layouts)."""
    delta_html = ""
    if delta:
        color_map = {"normal": "var(--color-text-secondary)", "success": "var(--color-success)",
                     "error": "var(--color-error)", "warning": "var(--color-warning)"}
        delta_html = f'<div style="font-size: {TYPOGRAPHY["size_sm"]}; font-weight: {TYPOGRAPHY["weight_medium"]}; color: {color_map.get(delta_color, "var(--color-text-secondary)")}; margin-top: {SPACE[1]};">{delta}</div>'

    return f"""
    <div class="card" style="padding: {SPACE['4']};">
        <div style="font-size: {TYPOGRAPHY['size_sm']}; font-weight: {TYPOGRAPHY['weight_medium']};
                    color: var(--color-text-secondary); margin-bottom: {SPACE[1]};">{label}</div>
        <div style="font-size: {TYPOGRAPHY['size_2xl']}; font-weight: {TYPOGRAPHY['weight_bold']};
                    color: var(--color-text-primary); font-family: var(--font-mono);">{value}</div>
        {delta_html}
    </div>
    """


def info_card(title: str, content: str, icon: str = ""):
    """Render an info card."""
    icon_html = f'<div style="width: 40px; height: 40px; border-radius: var(--radius-lg); background: var(--color-accent-light); display: flex; align-items: center; justify-content: center; font-size: 1.25rem; margin-bottom: {SPACE[3]};">{icon}</div>' if icon else ""
    return f"""
    <div class="card">
        {icon_html}
        <h3 class="card-title">{title}</h3>
        <p class="card-subtitle">{content}</p>
    </div>
    """


def badge(text: str, variant: str = "default"):
    """Render a badge/tag."""
    variants = {
        "default": "var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border-subtle)",
        "primary": "var(--color-accent-light); color: var(--color-accent); border: 1px solid var(--color-accent-border)",
        "success": "var(--color-success-bg); color: var(--color-success); border: 1px solid var(--color-success-border)",
        "warning": "var(--color-warning-bg); color: var(--color-warning); border: 1px solid var(--color-warning-border)",
        "error": "var(--color-error-bg); color: var(--color-error); border: 1px solid var(--color-error-border)",
        "info": "var(--color-info-bg); color: var(--color-info); border: 1px solid var(--color-info-border)",
    }
    style = variants.get(variant, variants["default"])
    return f'<span style="display: inline-block; padding: {SPACE[1]} {SPACE[2]}; font-size: {TYPOGRAPHY["size_xs"]}; font-weight: {TYPOGRAPHY["weight_medium"]}; border-radius: var(--radius-full); background: {style};">{text}</span>'


def divider():
    """Render a styled divider."""
    st.markdown('<hr class="divider">', unsafe_allow_html=True)


def card_container():
    """Context manager for a card container."""
    class CardContext:
        def __enter__(self):
            st.markdown('<div class="card">', unsafe_allow_html=True)
        def __exit__(self, *args):
            st.markdown('</div>', unsafe_allow_html=True)
    return CardContext()


# ─── Component Helpers ────────────────────────────────────────

def feature_grid(items: list, cols: int = 3):
    """Render a grid of feature cards."""
    columns = st.columns(cols)
    for i, item in enumerate(items):
        with columns[i % cols]:
            icon = item.get("icon", "")
            title = item.get("title", "")
            description = item.get("description", "")
            st.markdown(f"""
            <div class="card card-interactive animate-fade-in" style="animation-delay: {i * 100}ms; height: 100%;">
                {f'<div style="font-size: 1.5rem; margin-bottom: {SPACE[3]};">{icon}</div>' if icon else ''}
                <h3 style="margin: 0 0 {SPACE[2]} 0;">{title}</h3>
                <p style="margin: 0; color: var(--color-text-secondary);">{description}</p>
            </div>
            """, unsafe_allow_html=True)


def stat_row(metrics: list):
    """Render a row of metric cards."""
    cols = st.columns(len(metrics))
    for i, (label, value, delta, delta_color) in enumerate(metrics):
        with cols[i]:
            st.markdown(metric_card(label, value, delta, delta_color), unsafe_allow_html=True)


def two_column_layout(left_content, right_content, ratio: tuple = (2, 1)):
    """Render a two-column layout with content functions."""
    col1, col2 = st.columns(ratio)
    with col1:
        left_content()
    with col2:
        right_content()