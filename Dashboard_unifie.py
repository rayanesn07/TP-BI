#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTELLIGENCE COMMERCIALE — DASHBOARD UNIFIÉ v1.0
Ventes · Achats · Marges
Design: Dark Editorial — Charcoal × Gold × Ivory
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os, io, re
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG  (appelé une seule fois)
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Intelligence Commerciale",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  PALETTES PAR MODULE
# ══════════════════════════════════════════════════════════════
THEMES = {
    "ventes": {
        "accent":     "#C9A84C",
        "accent_lt":  "#E8C97A",
        "icon":       "◆",
        "label":      "VENTES",
        "gradient":   "rgba(201,168,76,0.25)",
        "grad_end":   "rgba(201,168,76,1)",
    },
    "achats": {
        "accent":     "#C9821E",
        "accent_lt":  "#E8A84C",
        "icon":       "◈",
        "label":      "ACHATS",
        "gradient":   "rgba(201,130,30,0.25)",
        "grad_end":   "rgba(201,130,30,1)",
    },
    "marges": {
        "accent":     "#16A085",
        "accent_lt":  "#1ABC9C",
        "icon":       "◇",
        "label":      "MARGES",
        "gradient":   "rgba(22,160,133,0.25)",
        "grad_end":   "rgba(22,160,133,1)",
    },
}

# Palette de base commune
C = {
    "bg":        "#0F0F0F",
    "surface":   "#161616",
    "card":      "#1C1C1C",
    "card2":     "#212121",
    "border":    "#2A2A2A",
    "border2":   "#333333",
    "ivory":     "#F0EAD6",
    "ivory_dim": "#A89F8C",
    "red":       "#C0392B",
    "green":     "#27AE60",
    "blue":      "#2980B9",
    "teal":      "#16A085",
    "text":      "#E8E3DA",
    "text_dim":  "#7A7469",
    "text_muted":"#3D3A35",
}

PALETTE = ["#C9A84C","#E8C97A","#C9821E","#2980B9","#16A085",
           "#27AE60","#C0392B","#8E44AD","#D35400","#1A5276"]

MOIS_FR = {1:"Jan",2:"Fév",3:"Mar",4:"Avr",5:"Mai",6:"Jun",
           7:"Jul",8:"Aoû",9:"Sep",10:"Oct",11:"Nov",12:"Déc"}

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
CSV_VENTES    = os.path.join(SCRIPT_DIR, "ventes.csv")
CSV_ACHATS    = os.path.join(SCRIPT_DIR, "achats.csv")
EXCEL_MARGES  = os.path.join(SCRIPT_DIR, "tableau3_complet.xlsx")

# ══════════════════════════════════════════════════════════════
#  GRADIENT HELPERS
# ══════════════════════════════════════════════════════════════
def grad_colors(n, start="rgba(33,33,33,1)", end="rgba(201,168,76,1)"):
    if n == 0: return []
    if n == 1: return [end]
    def parse(c):
        m = re.match(r'rgba\((\d+),(\d+),(\d+),([\d.]+)\)', c)
        return [int(m.group(i)) for i in range(1, 4)] + [float(m.group(4))]
    s, e = parse(start), parse(end)
    result = []
    for i in range(n):
        t = i / (n - 1)
        r = [int(s[j] + t*(e[j]-s[j])) for j in range(3)] + [round(s[3] + t*(e[3]-s[3]), 2)]
        result.append(f"rgba({r[0]},{r[1]},{r[2]},{r[3]})")
    return result

def grad_gold(n):   return grad_colors(n, "rgba(33,33,33,1)", "rgba(201,168,76,1)")
def grad_amber(n):  return grad_colors(n, "rgba(33,33,33,1)", "rgba(201,130,30,1)")
def grad_teal(n):   return grad_colors(n, "rgba(33,33,33,1)", "rgba(22,160,133,1)")
def grad_red(n):    return grad_colors(n, "rgba(33,33,33,1)", "rgba(192,57,43,1)")

def grad_for(module, n):
    if module == "ventes": return grad_gold(n)
    if module == "achats": return grad_amber(n)
    return grad_teal(n)

# ══════════════════════════════════════════════════════════════
#  CSS UNIFIÉ
# ══════════════════════════════════════════════════════════════
def inject_css(accent, accent_lt):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=DM+Mono:wght@300;400;500&family=Bebas+Neue&display=swap');

    *, *::before, *::after {{ box-sizing: border-box; }}
    html, body, [data-testid="stAppViewContainer"] {{
        background: {C['bg']} !important;
        color: {C['text']};
    }}
    [data-testid="stAppViewContainer"] > .main {{
        background: {C['bg']} !important;
        padding-top: 0 !important;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; display:none; }}

    /* ── CACHER BOUTON COLLAPSE SIDEBAR ── */
    [data-testid="stSidebarCollapseButton"],
    button[data-testid="stBaseButton-header"],
    [data-testid="stSidebarCollapsedControl"],
    [class*="collapsedControl"],
    [class*="collapse"] svg {{ display: none !important; }}
    .block-container {{ padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }}

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {{
        background: {C['surface']} !important;
        border-right: 1px solid {C['border']} !important;
    }}
    [data-testid="stSidebar"] * {{
        font-family: 'DM Mono', monospace !important;
        color: {C['text']};
    }}
    [data-testid="stSidebar"] label {{
        color: {C['ivory_dim']} !important;
        font-size: 10px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }}

    /* ── SELECTBOX ── */
    .stSelectbox > div > div {{
        background: {C['card']} !important;
        border: 1px solid {C['border2']} !important;
        border-radius: 0 !important;
        color: {C['text']} !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 12px !important;
    }}
    .stSelectbox > div > div:focus-within {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 1px {accent} !important;
    }}
    [data-baseweb="popover"], [data-baseweb="menu"] {{
        background: {C['card2']} !important;
        border: 1px solid {C['border2']} !important;
        border-radius: 0 !important;
    }}
    [data-baseweb="option"] {{
        background: {C['card2']} !important;
        color: {C['text']} !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 11px !important;
    }}
    [data-baseweb="option"]:hover {{
        background: {C['card']} !important;
        color: {accent} !important;
    }}

    /* ── DATE INPUT ── */
    [data-testid="stDateInput"] > div,
    [data-testid="stDateInput"] input {{
        background: {C['card']} !important;
        border: 1px solid {C['border2']} !important;
        border-radius: 0 !important;
        color: {C['text']} !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 11px !important;
    }}
    [data-testid="stDateInput"] > label {{
        color: {C['ivory_dim']} !important;
        font-size: 10px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }}

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {C['surface']};
        border-bottom: 1px solid {C['border2']};
        gap: 0; padding: 0;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: {C['text_dim']} !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-bottom: 2px solid transparent !important;
        padding: 14px 24px !important;
        border-radius: 0 !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {accent} !important;
        border-bottom: 2px solid {accent} !important;
        background: {C['card']} !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        background: {C['bg']}; padding: 0 !important;
    }}

    /* ── BUTTON ── */
    .stButton > button {{
        background: transparent !important;
        color: {accent} !important;
        border: 1px solid {accent} !important;
        border-radius: 0 !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        padding: 8px 20px !important;
    }}
    .stButton > button:hover {{
        background: {accent}18 !important;
    }}

    /* ── RADIO ── */
    .stRadio label {{
        color: {C['text_dim']} !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 11px !important;
    }}
    .stRadio [data-baseweb="radio"] div {{
        background: {C['card']} !important;
        border-color: {C['border2']} !important;
    }}

    /* ── SLIDER ── */
    [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {{
        background: {accent} !important;
        border-color: {accent} !important;
    }}

    /* ── DATAFRAME ── */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > div {{
        background: {C['card']} !important;
        border: 1px solid {C['border']} !important;
        border-radius: 0 !important;
    }}

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar {{ width: 4px; height: 4px; }}
    ::-webkit-scrollbar-track {{ background: {C['bg']}; }}
    ::-webkit-scrollbar-thumb {{ background: {C['border2']}; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {accent}66; }}

    /* ── MISC ── */
    #MainMenu, footer {{ visibility: hidden; }}
    /* stToolbar visible pour Deploy */
    div[data-testid="column"] {{ background: transparent !important; }}
    .element-container {{ background: transparent !important; }}
    p, span {{ font-family: 'DM Mono', monospace; }}
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  HELPERS COMMUNS
# ══════════════════════════════════════════════════════════════
def fmt(v):
    if pd.isna(v): return "—"
    return f"{v:,.0f} DA".replace(",", " ")

def fmt_pct(v):
    if pd.isna(v): return "—"
    return f"{v*100:.1f}%" if v < 2 else f"{v:.1f}%"

def dark_table(df, height=400):
    """Tableau HTML entièrement dark, unifié pour les 3 modules."""
    cols = df.columns.tolist()
    th = "".join(
        f'<th style="padding:8px 14px;text-align:left;font-family:\'DM Mono\',monospace;'
        f'font-size:9px;letter-spacing:2px;text-transform:uppercase;color:{C["text_dim"]};'
        f'border-bottom:1px solid {C["border2"]};white-space:nowrap;background:{C["card2"]};">'
        f'{c}</th>'
        for c in cols
    )
    rows_html = ""
    for i, (_, row) in enumerate(df.iterrows()):
        bg = C['card'] if i % 2 == 0 else C['card2']
        tds = "".join(
            f'<td style="padding:7px 14px;font-family:\'DM Mono\',monospace;'
            f'font-size:11px;color:{C["ivory_dim"]};border-bottom:1px solid {C["border"]};'
            f'white-space:nowrap;">{v}</td>'
            for v in row.values
        )
        rows_html += f'<tr style="background:{bg};">{tds}</tr>'

    st.markdown(f"""
    <div style="overflow-y:auto;overflow-x:auto;max-height:{height}px;
                border:1px solid {C['border']};background:{C['card']};">
      <table style="width:100%;border-collapse:collapse;">
        <thead><tr>{th}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

def chart_layout(fig, height=380, margin=None, show_legend=True):
    m = margin or dict(l=40, r=20, t=30, b=40)
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=C['card'],
        font=dict(family="DM Mono", color=C['ivory_dim'], size=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=C['border2'], borderwidth=1,
            font=dict(size=9, color=C['ivory_dim']),
            visible=show_legend,
        ),
        xaxis=dict(
            gridcolor=C['border'], gridwidth=1,
            linecolor=C['border2'], tickfont=dict(size=9, color=C['text_dim']),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=C['border'], gridwidth=1,
            linecolor=C['border2'], tickfont=dict(size=9, color=C['text_dim']),
            zeroline=False,
        ),
        margin=m,
    )
    return fig

def card_html(label, value, color):
    return (
        f'<div style="background:{C["card2"]};border-left:3px solid {color};padding:16px 20px;">'
        f'<div style="font-family:\'DM Mono\',monospace;font-size:9px;letter-spacing:3px;'
        f'color:{C["text_dim"]};text-transform:uppercase;margin-bottom:8px;">{label}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:26px;color:{color};'
        f'line-height:1;letter-spacing:2px;">{value}</div>'
        f'</div>'
    )

def kpis(items):
    cols = st.columns(len(items))
    for c, (lbl, val, color) in zip(cols, items):
        c.markdown(card_html(lbl, val, color), unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

def section_hdr(title, subtitle="", accent_color=None):
    accent_color = accent_color or C['ivory_dim']
    sub_html = (
        f'<span style="font-family:DM Mono,monospace;font-size:9px;'
        f'color:{C["text_dim"]};letter-spacing:2px;">{subtitle}</span>'
    ) if subtitle else ""
    grad = accent_color.replace("#", "")
    # Convert hex to rgba
    r, g, b = int(grad[0:2],16), int(grad[2:4],16), int(grad[4:6],16)
    html = (
        f'<div style="margin:24px 0 14px;display:flex;align-items:center;gap:16px;'
        f'border-bottom:1px solid {C["border"]};padding-bottom:10px;">'
        f'<span style="font-family:Bebas Neue,sans-serif;font-size:20px;'
        f'color:{C["ivory"]};letter-spacing:3px;white-space:nowrap;">{title}</span>'
        + sub_html +
        f'<div style="flex:1;height:1px;'
        f'background:linear-gradient(90deg,rgba({r},{g},{b},0.3),transparent);'
        f'margin-left:8px;"></div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def hero_banner(title_label, title_value, metrics, accent):
    items_html = ""
    for label, value, color in metrics:
        items_html += (
            f'<div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:22px;color:{color};">{value}</div>'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:9px;color:{C["text_dim"]};letter-spacing:2px;">{label}</div>'
            f'</div>'
        )
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{C['card2']} 0%,{C['card']} 100%);
                border-left:4px solid {accent};border-bottom:1px solid {C['border2']};
                padding:28px 32px;margin-bottom:24px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-10px;right:40px;
                    font-family:'Bebas Neue',sans-serif;font-size:110px;
                    color:{accent}07;letter-spacing:8px;pointer-events:none;">N°1</div>
        <div style="font-family:'DM Mono',monospace;font-size:9px;
                    color:{C['text_dim']};letter-spacing:4px;margin-bottom:10px;">{title_label}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:40px;
                    color:{C['ivory']};letter-spacing:5px;line-height:1;">{title_value.upper()}</div>
        <div style="display:flex;gap:48px;margin-top:20px;flex-wrap:wrap;">{items_html}</div>
    </div>
    """, unsafe_allow_html=True)

def empty_state(icon, msg):
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;height:50vh;gap:16px;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:60px;color:{C['border2']};">{icon}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:22px;
                    color:{C['ivory_dim']};letter-spacing:4px;">{msg}</div>
    </div>""", unsafe_allow_html=True)

def no_filter_result():
    st.markdown(f"""
    <div style="text-align:center;padding:80px;font-family:'DM Mono',monospace;">
        <div style="font-size:32px;color:{C['red']};">⚠</div>
        <div style="color:{C['ivory_dim']};margin-top:12px;letter-spacing:2px;">
            Aucun résultat pour ces filtres</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  CHARGEMENT DONNÉES
# ══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_ventes():
    df = pd.read_csv(CSV_VENTES)
    df['Date.CMD']    = pd.to_datetime(df['Date.CMD'])
    df['Mois']        = df['Date.CMD'].dt.month
    df['Annee']       = df['Date.CMD'].dt.year
    df['Mois_Nom']    = df['Date.CMD'].dt.strftime('%b')
    df['Client_Full'] = df['Forme_Juridique'].str.strip() + ' ' + df['Client'].str.strip()
    return df

@st.cache_data(show_spinner=False)
def load_achats():
    df = pd.read_csv(CSV_ACHATS)
    df['Date.CMD'] = pd.to_datetime(df['Date.CMD'])
    df['Mois']     = df['Date.CMD'].dt.month
    df['Annee']    = df['Date.CMD'].dt.year
    df['Mois_Nom'] = df['Date.CMD'].dt.strftime('%b')
    return df

@st.cache_data(show_spinner=False)
def load_marges():
    df = pd.read_excel(EXCEL_MARGES)
    df.columns = df.columns.str.strip()
    df['Date_commande'] = pd.to_datetime(df['Date_commande'])
    df['Mois']     = df['Date_commande'].dt.month
    df['Annee']    = df['Date_commande'].dt.year
    df['Mois_Nom'] = df['Mois'].map(MOIS_FR)
    for col in ['MargeTotale','MargeUnitaire','Montant HT','Montant TTC','Taux Marge %','quantité','PMP']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


# ══════════════════════════════════════════════════════════════
#  NAVIGATION SIDEBAR
# ══════════════════════════════════════════════════════════════
def render_nav():
    # Initialiser session_state si absent
    if "active_module" not in st.session_state:
        st.session_state.active_module = "ventes"

    with st.sidebar:
        # ── En-tête ──────────────────────────────────────────
        st.markdown(f"""
        <div style="padding:28px 16px 16px;">
            <div style="font-family:'DM Mono',monospace;font-size:8px;
                        color:{C['text_dim']};letter-spacing:6px;margin-bottom:6px;">
                INTELLIGENCE COMMERCIALE</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:28px;
                        color:{C['ivory']};letter-spacing:5px;line-height:1;">DASHBOARD</div>
            <div style="font-family:'DM Mono',monospace;font-size:9px;
                        color:{C['text_dim']};margin-top:4px;">
                {datetime.now().strftime('%d · %m · %Y')}</div>
        </div>
        <div style="height:1px;background:linear-gradient(90deg,
            {THEMES['ventes']['accent']},{THEMES['achats']['accent']},{THEMES['marges']['accent']},transparent);
            margin:0 16px 0 16px;"></div>
        <div style="font-family:'DM Mono',monospace;font-size:9px;
            color:{C['text_dim']};letter-spacing:3px;padding:20px 16px 10px;">NAVIGATION</div>
        """, unsafe_allow_html=True)

        # ── Boutons de navigation ─────────────────────────────
        nav_items = [
            ("ventes", "◆", "VENTES",  THEMES["ventes"]["accent"]),
            ("achats", "◈", "ACHATS",  THEMES["achats"]["accent"]),
            ("marges", "◇", "MARGES",  THEMES["marges"]["accent"]),
        ]

        for module_id, icon, label, color in nav_items:
            is_active = st.session_state.active_module == module_id
            bg      = color + "22" if is_active else "transparent"
            border  = f"2px solid {color}" if is_active else f"1px solid {C['border2']}"
            txt_clr = color if is_active else C['ivory_dim']

            st.markdown(f"""
            <style>
            div[data-testid="stButton"] > button#btn_{module_id} {{
                background: {bg} !important;
                color: {txt_clr} !important;
                border: {border} !important;
                border-radius: 0 !important;
                font-family: 'DM Mono', monospace !important;
                font-size: 12px !important;
                letter-spacing: 3px !important;
                text-transform: uppercase !important;
                padding: 12px 20px !important;
                width: 100% !important;
                text-align: left !important;
                margin-bottom: 4px !important;
                cursor: pointer !important;
                transition: all 0.15s ease !important;
            }}
            </style>
            """, unsafe_allow_html=True)

            if st.button(f"{icon}  {label}", key=f"btn_{module_id}",
                         width='stretch'):
                st.session_state.active_module = module_id
                st.rerun()

        # ── Séparateur ────────────────────────────────────────
        st.markdown(f"""
        <div style="height:1px;background:{C['border']};margin:16px 0;"></div>
        """, unsafe_allow_html=True)

    return st.session_state.active_module


# ══════════════════════════════════════════════════════════════
#  MASTHEAD DYNAMIQUE
# ══════════════════════════════════════════════════════════════
def render_masthead(module):
    th = THEMES[module]
    accent    = th["accent"]
    accent_lt = th["accent_lt"]
    icon      = th["icon"]
    label     = th["label"]
    st.markdown(f"""
    <div style="background:{C['surface']};padding:20px 32px;
                border-bottom:1px solid {C['border2']};margin-bottom:0;">
        <div style="display:flex;align-items:baseline;gap:20px;">
            <span style="font-family:'DM Mono',monospace;font-size:9px;
                         color:{accent};letter-spacing:6px;">{icon}</span>
            <span style="font-family:'Bebas Neue',sans-serif;font-size:26px;
                         color:{C['ivory']};letter-spacing:6px;">{label} INTELLIGENCE</span>
            <span style="font-family:'DM Mono',monospace;font-size:10px;color:{C['text_dim']};">
                · v1.0 · {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        </div>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,
        {accent},{accent_lt},{accent}44,transparent);"></div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SIDEBAR FILTRES — VENTES
# ══════════════════════════════════════════════════════════════
def sidebar_ventes(df):
    accent = THEMES["ventes"]["accent"]
    with st.sidebar:
        st.markdown(f"""<div style="font-family:'DM Mono',monospace;font-size:9px;
            color:{accent};letter-spacing:3px;padding:20px 0 8px;">FILTRES</div>""",
            unsafe_allow_html=True)

        d_min = df['Date.CMD'].min().date()
        d_max = df['Date.CMD'].max().date()
        date_rng = st.date_input("Période", value=(d_min, d_max),
                                  min_value=d_min, max_value=d_max, key="v_date")

        filters = {}
        for lbl, col, key in [
            ("Produit",      "Produit",         "v_prod"),
            ("Catégorie",    "Categorie",        "v_cat"),
            ("Client",       "Client",           "v_cli"),
            ("Forme Jur.",   "Forme_Juridique",  "v_fj"),
            ("Type Vente",   "Type_Vente",       "v_tv"),
            ("Wilaya",       "Wilaya",           "v_wil"),
        ]:
            opts = ["— Tous —"] + sorted(df[col].dropna().unique().tolist())
            filters[col] = st.selectbox(lbl, opts, index=0, key=key)

        if st.button("↺  Réinitialiser", width='stretch', key="v_reset"):
            st.rerun()

        st.markdown(f"""
        <div style="margin-top:20px;padding:14px 16px;background:{C['card2']};
                    border-top:2px solid {accent}44;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:20px;
                        color:{accent};letter-spacing:2px;">{fmt(df['Montant_HT'].sum())}</div>
            <div style="font-family:'DM Mono',monospace;font-size:9px;
                        color:{C['text_dim']};margin-top:2px;">CA HT TOTAL</div>
            <div style="height:1px;background:{C['border']};margin:8px 0;"></div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:14px;
                        color:{C['ivory_dim']};">{df['Num.CMD'].nunique()} commandes</div>
        </div>
        """, unsafe_allow_html=True)

    return filters, date_rng


# ══════════════════════════════════════════════════════════════
#  SIDEBAR FILTRES — ACHATS
# ══════════════════════════════════════════════════════════════
def sidebar_achats(df):
    accent = THEMES["achats"]["accent"]
    with st.sidebar:
        st.markdown(f"""<div style="font-family:'DM Mono',monospace;font-size:9px;
            color:{accent};letter-spacing:3px;padding:20px 0 8px;">FILTRES</div>""",
            unsafe_allow_html=True)

        d_min = df['Date.CMD'].min().date()
        d_max = df['Date.CMD'].max().date()
        date_rng = st.date_input("Période", value=(d_min, d_max),
                                  min_value=d_min, max_value=d_max, key="a_date")

        filters = {}
        for lbl, col, key in [
            ("Produit",     "Produit",     "a_prod"),
            ("Catégorie",   "Categorie",   "a_cat"),
            ("Fournisseur", "Fournisseur", "a_four"),
            ("Type Achat",  "Type_Achat",  "a_ta"),
            ("Année",       "Annee",       "a_ann"),
            ("Mois",        "Mois",        "a_mois"),
        ]:
            opts = ["— Tous —"] + sorted(df[col].dropna().astype(str).unique().tolist())
            filters[col] = st.selectbox(lbl, opts, index=0, key=key)

        if st.button("↺  Réinitialiser", width='stretch', key="a_reset"):
            st.rerun()

        st.markdown(f"""
        <div style="margin-top:20px;padding:14px 16px;background:{C['card2']};
                    border-top:2px solid {accent}44;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:20px;
                        color:{accent};letter-spacing:2px;">{fmt(df['Montant_HT'].sum())}</div>
            <div style="font-family:'DM Mono',monospace;font-size:9px;
                        color:{C['text_dim']};margin-top:2px;">COÛT HT TOTAL</div>
            <div style="height:1px;background:{C['border']};margin:8px 0;"></div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:14px;
                        color:{C['ivory_dim']};">{df['Num.CMD'].nunique()} commandes</div>
        </div>
        """, unsafe_allow_html=True)

    return filters, date_rng


# ══════════════════════════════════════════════════════════════
#  SIDEBAR FILTRES — MARGES
# ══════════════════════════════════════════════════════════════
def sidebar_marges(df_all):
    accent = THEMES["marges"]["accent"]
    ventes = df_all[df_all['type_commande'] == 'VENTE']
    with st.sidebar:
        st.markdown(f"""<div style="font-family:'DM Mono',monospace;font-size:9px;
            color:{accent};letter-spacing:3px;padding:20px 0 8px;">FILTRES</div>""",
            unsafe_allow_html=True)

        d_min = df_all['Date_commande'].min().date()
        d_max = df_all['Date_commande'].max().date()
        date_rng = st.date_input("Période", value=(d_min, d_max),
                                  min_value=d_min, max_value=d_max, key="m_date")

        filters = {}
        for lbl, col, key in [
            ("Produit",   "produit",        "m_prod"),
            ("Catégorie", "Catégorie",       "m_cat"),
            ("Wilaya",    "Wilaya",          "m_wil"),
            ("Type",      "type_commande",   "m_type"),
        ]:
            opts = ["— Tous —"] + sorted(ventes[col].dropna().unique().tolist())
            filters[col] = st.selectbox(lbl, opts, index=0, key=key)

        if st.button("↺  Réinitialiser", width='stretch', key="m_reset"):
            st.rerun()

        mt = ventes['MargeTotale'].sum()
        nb = len(ventes)
        st.markdown(f"""
        <div style="margin-top:20px;padding:14px 16px;background:{C['card2']};
                    border-top:2px solid {accent}44;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:20px;
                        color:{accent};letter-spacing:2px;">{fmt(mt)}</div>
            <div style="font-family:'DM Mono',monospace;font-size:9px;
                        color:{C['text_dim']};margin-top:2px;">MARGE TOTALE VENTES</div>
            <div style="height:1px;background:{C['border']};margin:8px 0;"></div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:14px;
                        color:{C['ivory_dim']};">{nb} lignes de vente</div>
        </div>
        """, unsafe_allow_html=True)

    return filters, date_rng


# ══════════════════════════════════════════════════════════════
#  APPLY FILTERS
# ══════════════════════════════════════════════════════════════
def apply_filters_ventes(df, filters, date_rng):
    out = df.copy()
    if isinstance(date_rng, (list, tuple)) and len(date_rng) == 2:
        out = out[(out['Date.CMD'].dt.date >= date_rng[0]) &
                  (out['Date.CMD'].dt.date <= date_rng[1])]
    for col, val in filters.items():
        if val != "— Tous —":
            out = out[out[col] == val]
    return out

def apply_filters_achats(df, filters, date_rng):
    out = df.copy()
    if isinstance(date_rng, (list, tuple)) and len(date_rng) == 2:
        out = out[(out['Date.CMD'].dt.date >= date_rng[0]) &
                  (out['Date.CMD'].dt.date <= date_rng[1])]
    for col, val in filters.items():
        if val != "— Tous —":
            out = out[out[col].astype(str) == val]
    return out

def apply_filters_marges(df, filters, date_rng):
    out = df.copy()
    if isinstance(date_rng, (list, tuple)) and len(date_rng) == 2:
        out = out[(out['Date_commande'].dt.date >= date_rng[0]) &
                  (out['Date_commande'].dt.date <= date_rng[1])]
    for col, val in filters.items():
        if val != "— Tous —":
            out = out[out[col] == val]
    return out


# ══════════════════════════════════════════════════════════════
#  ████  MODULE VENTES  ████
# ══════════════════════════════════════════════════════════════
ACC_V = THEMES["ventes"]["accent"]

def v_tab_overview(df):
    total_ca  = df['Montant_HT'].sum()
    total_ttc = df['Montant_TTC'].sum()
    nb_cmd    = df['Num.CMD'].nunique()
    nb_cli    = df['Client'].nunique()
    nb_prod   = df['Produit'].nunique()
    panier    = total_ca / nb_cmd if nb_cmd else 0

    kpis([
        ("CA Hors Taxes",  fmt(total_ca),  ACC_V),
        ("CA TTC",         fmt(total_ttc), C['ivory_dim']),
        ("Panier Moyen",   fmt(panier),    C['teal']),
        ("Commandes",      str(nb_cmd),    C['blue']),
        ("Clients Actifs", str(nb_cli),    C['green']),
        ("Produits",       str(nb_prod),   C['red']),
    ])

    col1, col2 = st.columns([3, 2])
    with col1:
        section_hdr("ÉVOLUTION MENSUELLE", "CA HT + Quantités", ACC_V)
        dm = df.copy()
        dm['M'] = dm['Date.CMD'].dt.to_period('M').dt.to_timestamp()
        mon = dm.groupby('M').agg(CA=('Montant_HT','sum'), Qte=('Qte','sum')).reset_index()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=mon['M'], y=mon['CA'], name="CA HT",
            marker_color=ACC_V, marker_line_width=0, opacity=0.85), secondary_y=False)
        fig.add_trace(go.Scatter(x=mon['M'], y=mon['Qte'], name="Quantités",
            mode='lines+markers', line=dict(color=C['teal'], width=2),
            marker=dict(size=5, color=C['teal'])), secondary_y=True)
        chart_layout(fig, height=300)
        fig.update_yaxes(tickfont=dict(color=ACC_V, size=9), secondary_y=False, showgrid=True)
        fig.update_yaxes(tickfont=dict(color=C['teal'], size=9), secondary_y=True, showgrid=False)
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(fig, width='stretch')

    with col2:
        section_hdr("PAR CATÉGORIE", "Répartition CA", ACC_V)
        cat = df.groupby('Categorie')['Montant_HT'].sum().sort_values(ascending=False).reset_index()
        fig2 = go.Figure(go.Pie(labels=cat['Categorie'], values=cat['Montant_HT'],
            marker_colors=PALETTE[:len(cat)], hole=0.55,
            textfont=dict(family="DM Mono", size=10),
            marker=dict(line=dict(color=C['bg'], width=2))))
        fig2.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(font=dict(family="DM Mono",size=9,color=C['ivory_dim']),bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(text=f"<b>{len(cat)}</b><br>cat.", x=0.5, y=0.5,
                font=dict(family="Bebas Neue",size=22,color=C['ivory']), showarrow=False)])
        st.plotly_chart(fig2, width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        section_hdr("TOP 10 PRODUITS", "par CA HT", ACC_V)
        top10 = df.groupby('Produit')['Montant_HT'].sum().nlargest(10).sort_values().reset_index()
        fig3 = go.Figure(go.Bar(x=top10['Montant_HT'], y=top10['Produit'], orientation='h',
            marker=dict(color=grad_gold(len(top10)), line=dict(width=0)),
            text=[fmt(v) for v in top10['Montant_HT']], textposition='outside',
            textfont=dict(size=9, color=C['text_dim'])))
        chart_layout(fig3, height=320, margin=dict(l=10,r=80,t=10,b=20), show_legend=False)
        fig3.update_xaxes(showgrid=False, showticklabels=False)
        fig3.update_yaxes(tickfont=dict(size=10, color=C['ivory_dim']))
        st.plotly_chart(fig3, width='stretch')

    with col4:
        section_hdr("TOP 10 CLIENTS", "par CA HT", ACC_V)
        top_cli = df.groupby('Client_Full')['Montant_HT'].sum().nlargest(10).sort_values().reset_index()
        fig4 = go.Figure(go.Bar(x=top_cli['Montant_HT'], y=top_cli['Client_Full'], orientation='h',
            marker=dict(color=grad_teal(len(top_cli)), line=dict(width=0)),
            text=[fmt(v) for v in top_cli['Montant_HT']], textposition='outside',
            textfont=dict(size=9, color=C['text_dim'])))
        chart_layout(fig4, height=320, margin=dict(l=10,r=90,t=10,b=20), show_legend=False)
        fig4.update_xaxes(showgrid=False, showticklabels=False)
        fig4.update_yaxes(tickfont=dict(size=9, color=C['ivory_dim']))
        st.plotly_chart(fig4, width='stretch')

def v_tab_analyse(df):
    GROUPS  = ["Produit","Categorie","Client","Forme_Juridique","Type_Vente","Wilaya","Mois","Annee"]
    METRICS = ["Montant_HT","Montant_TTC","Qte"]
    CHARTS  = ["Barres","Barres H","Ligne","Camembert","Treemap"]

    c1,c2,c3,c4,c5 = st.columns([2,2,2,2,1])
    with c1: grp    = st.selectbox("Axe X", GROUPS, key="va_grp")
    with c2: met    = st.selectbox("Mesure", METRICS, key="va_met")
    with c3: chtype = st.selectbox("Graphique", CHARTS, key="va_cht")
    with c4: tri    = st.radio("Tri", ["↓ Desc","↑ Asc"], horizontal=True, key="va_tri")
    with c5: topn   = st.slider("Top N", 5, 30, 15, key="va_n")

    agg = df.groupby(grp)[met].sum().sort_values(ascending=(tri=="↑ Asc")).reset_index()
    agg_top = agg.head(topn)
    total = agg[met].sum()
    is_money = "Montant" in met

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    kpis([
        ("Total " + met.replace("_"," "), fmt(total) if is_money else f"{int(total):,}", ACC_V),
        ("Lignes",    str(len(df)),                C['blue']),
        ("Commandes", str(df['Num.CMD'].nunique()), C['teal']),
        ("Clients",   str(df['Client'].nunique()),  C['green']),
    ])

    col_t, col_c = st.columns([1, 2])
    with col_t:
        section_hdr("DONNÉES", f"{grp} / {met}", ACC_V)
        disp = agg_top.copy()
        disp['Part %'] = (disp[met] / total * 100).round(1).astype(str) + "%"
        disp[met] = disp[met].apply(fmt) if is_money else disp[met].astype(int)
        dark_table(disp, height=450)

    with col_c:
        section_hdr("VISUALISATION", chtype.upper(), ACC_V)
        xs = agg_top[grp].astype(str); ys = agg_top[met]; clrs = PALETTE[:len(agg_top)]
        fig = _build_chart(chtype, xs, ys, clrs, is_money, ACC_V)
        chart_layout(fig, height=470, show_legend=(chtype=="Camembert"))
        st.plotly_chart(fig, width='stretch')

def v_tab_produits(df):
    kpis([
        ("Produits",    str(df['Produit'].nunique()),   ACC_V),
        ("CA HT Total", fmt(df['Montant_HT'].sum()),    C['green']),
        ("Qté Totale",  f"{int(df['Qte'].sum()):,}",   C['blue']),
        ("Commandes",   str(df['Num.CMD'].nunique()),    C['teal']),
    ])

    col1, col2 = st.columns(2)
    with col1:
        section_hdr("STATISTIQUES PRODUITS", accent_color=ACC_V)
        prod = df.groupby(['Produit','Categorie']).agg(
            CA_HT=('Montant_HT','sum'), Qte=('Qte','sum'), Cmds=('Num.CMD','nunique')
        ).reset_index().sort_values('CA_HT', ascending=False)
        prod['CA_HT'] = prod['CA_HT'].apply(fmt)
        prod.columns = ['Produit','Catégorie','CA HT','Qté','Cmds']
        dark_table(prod, height=340)

    with col2:
        section_hdr("DERNIÈRES VENTES", "100 lignes", ACC_V)
        det = df.sort_values('Date.CMD', ascending=False).head(100).copy()
        det = det[['Num.CMD','Date.CMD','Client_Full','Produit','Qte','Montant_HT','Wilaya']]
        det['Date.CMD']   = det['Date.CMD'].dt.strftime('%d/%m/%Y')
        det['Montant_HT'] = det['Montant_HT'].apply(fmt)
        det.columns = ['N° CMD','Date','Client','Produit','Qté','Montant HT','Wilaya']
        dark_table(det, height=340)

    section_hdr("ÉVOLUTION TOP 5 PRODUITS", "mensuel", ACC_V)
    top5 = df.groupby('Produit')['Montant_HT'].sum().nlargest(5).index.tolist()
    d = df[df['Produit'].isin(top5)].copy()
    d['M'] = d['Date.CMD'].dt.to_period('M').dt.to_timestamp()
    tl = d.groupby(['M','Produit'])['Montant_HT'].sum().reset_index()
    fig = px.line(tl, x='M', y='Montant_HT', color='Produit',
                  color_discrete_sequence=PALETTE, markers=True)
    fig.update_traces(line=dict(width=2), marker=dict(size=5))
    chart_layout(fig, height=280); fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, width='stretch')

    section_hdr("CA vs QUANTITÉ", "Scatter par produit", ACC_V)
    bubble = df.groupby('Produit').agg(CA=('Montant_HT','sum'),Qte=('Qte','sum'),Cmds=('Num.CMD','nunique')).reset_index()
    fig2 = go.Figure(go.Scatter(x=bubble['Qte'], y=bubble['CA'], mode='markers+text',
        text=bubble['Produit'], textposition='top center', textfont=dict(size=8, color=C['text_dim']),
        marker=dict(size=bubble['Cmds'].clip(6,40).tolist(), color=bubble['CA'].tolist(),
            colorscale=[[0,"rgb(33,33,33)"],[1,"rgb(201,168,76)"]], showscale=False,
            line=dict(width=0), opacity=0.85),
        hovertemplate="<b>%{text}</b><br>CA: %{y:,.0f}<br>Qté: %{x:,.0f}<extra></extra>"))
    chart_layout(fig2, height=320, show_legend=False)
    fig2.update_xaxes(title_text="Quantité", title_font=dict(size=9, color=C['text_dim']))
    fig2.update_yaxes(title_text="CA HT",    title_font=dict(size=9, color=C['text_dim']))
    st.plotly_chart(fig2, width='stretch')

def v_tab_clients(df):
    agg = (df.groupby(['Client_Full','Forme_Juridique','Wilaya'])
           .agg(CA=('Montant_HT','sum'), Cmds=('Num.CMD','nunique'), Prods=('Code_Produit','nunique'))
           .reset_index().sort_values('CA', ascending=False).reset_index(drop=True))

    kpis([
        ("Clients",    str(len(agg)),              ACC_V),
        ("CA HT",      fmt(agg['CA'].sum()),        C['green']),
        ("Moy/Client", fmt(agg['CA'].mean()),       C['blue']),
        ("Wilayas",    str(df['Wilaya'].nunique()), C['teal']),
    ])

    col1, col2 = st.columns([3, 2])
    with col1:
        section_hdr("CLASSEMENT CLIENTS", accent_color=ACC_V)
        d = agg.copy(); d.insert(0, '#', range(1, len(d)+1))
        d['CA HT'] = d['CA'].apply(fmt)
        d = d[['#','Client_Full','Forme_Juridique','Wilaya','CA HT','Cmds','Prods']]
        d.columns = ['#','Client','Forme Jur.','Wilaya','CA HT','Cmds','Prods']
        dark_table(d, height=480)

    with col2:
        section_hdr("PAR WILAYA", accent_color=ACC_V)
        w = df.groupby('Wilaya')['Montant_HT'].sum().sort_values(ascending=True).reset_index()
        fig = go.Figure(go.Bar(x=w['Montant_HT'], y=w['Wilaya'], orientation='h',
            marker=dict(color=w['Montant_HT'].tolist(),
                colorscale=[[0,"rgb(33,33,33)"],[1,"rgb(201,168,76)"]], showscale=False, line=dict(width=0))))
        chart_layout(fig, height=240, margin=dict(l=10,r=50,t=10,b=20), show_legend=False)
        fig.update_xaxes(showgrid=False, showticklabels=False)
        fig.update_yaxes(tickfont=dict(size=9))
        st.plotly_chart(fig, width='stretch')

        section_hdr("FORME JURIDIQUE", accent_color=ACC_V)
        fj = df.groupby('Forme_Juridique')['Montant_HT'].sum().reset_index()
        fig2 = go.Figure(go.Pie(labels=fj['Forme_Juridique'], values=fj['Montant_HT'],
            marker_colors=PALETTE[:len(fj)], hole=0.5,
            textfont=dict(family="DM Mono",size=10), marker=dict(line=dict(color=C['bg'],width=2))))
        fig2.update_layout(height=220, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=0,b=0),
            legend=dict(font=dict(family="DM Mono",size=9,color=C['ivory_dim']),bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig2, width='stretch')

    section_hdr("HEATMAP WILAYA × CATÉGORIE", "Intensité du CA", ACC_V)
    pivot = df.pivot_table(values='Montant_HT', index='Wilaya', columns='Categorie', aggfunc='sum', fill_value=0)
    fig3 = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale=[[0,"rgb(28,28,28)"],[0.5,"rgb(150,110,40)"],[1,"rgb(232,201,122)"]],
        showscale=True, xgap=2, ygap=2))
    chart_layout(fig3, height=280, margin=dict(l=10,r=20,t=10,b=40), show_legend=False)
    st.plotly_chart(fig3, width='stretch')

def v_tab_categories(df):
    agg = df.groupby('Categorie').agg(
        CA_HT=('Montant_HT','sum'), CA_TTC=('Montant_TTC','sum'),
        Qte=('Qte','sum'), Prods=('Code_Produit','nunique'), Cmds=('Num.CMD','nunique')
    ).reset_index().sort_values('CA_HT', ascending=False).reset_index(drop=True)
    if agg.empty: st.warning("Aucune donnée."); return

    best = agg.iloc[0]; total = agg['CA_HT'].sum()
    hero_banner("MEILLEURE CATÉGORIE", best['Categorie'], [
        ("CA HT",      fmt(best['CA_HT']),             ACC_V),
        ("PART DU CA", f"{best['CA_HT']/total*100:.1f}%", C['ivory_dim']),
        ("QTÉ VENDUE", f"{int(best['Qte']):,}",        C['teal']),
        ("COMMANDES",  str(int(best['Cmds'])),          C['blue']),
    ], ACC_V)

    col1, col2 = st.columns([1, 2])
    with col1:
        section_hdr("CLASSEMENT", accent_color=ACC_V)
        d = agg.copy(); d.insert(0,'#',[f"#{i+1}" for i in range(len(d))])
        d['Part %'] = (d['CA_HT']/total*100).round(1).astype(str)+"%"
        d['CA HT'] = d['CA_HT'].apply(fmt); d['Qté'] = d['Qte'].astype(int)
        d = d[['#','Categorie','CA HT','Part %','Qté','Cmds']]
        d.columns = ['#','Catégorie','CA HT','Part %','Qté','Cmds']
        dark_table(d, height=300)

    with col2:
        colors = PALETTE[:len(agg)]
        fig = make_subplots(rows=1,cols=2,specs=[[{"type":"pie"},{"type":"xy"}]])
        fig.add_trace(go.Pie(labels=agg['Categorie'], values=agg['CA_HT'],
            marker_colors=colors, hole=0.45, pull=[0.06 if i==0 else 0 for i in range(len(agg))],
            textfont=dict(family="DM Mono",size=10), marker=dict(line=dict(color=C['bg'],width=3))),row=1,col=1)
        fig.add_trace(go.Bar(x=agg['Categorie'], y=agg['CA_HT'],
            marker_color=colors, marker_line_width=0), row=1, col=2)
        chart_layout(fig, height=300, show_legend=False)
        fig.update_xaxes(tickangle=-20, row=1, col=2)
        st.plotly_chart(fig, width='stretch')

    section_hdr("ÉVOLUTION MENSUELLE", accent_color=ACC_V)
    dm = df.copy(); dm['M'] = dm['Date.CMD'].dt.to_period('M').dt.to_timestamp()
    cm = dm.groupby(['M','Categorie'])['Montant_HT'].sum().reset_index()
    fig2 = px.area(cm, x='M', y='Montant_HT', color='Categorie', color_discrete_sequence=PALETTE)
    fig2.update_traces(line=dict(width=1.5))
    chart_layout(fig2, height=280); st.plotly_chart(fig2, width='stretch')

    section_hdr("PARETO", accent_color=ACC_V)
    agg_p = agg.sort_values('CA_HT', ascending=False).copy()
    agg_p['cumul'] = agg_p['CA_HT'].cumsum() / total * 100
    fig3 = make_subplots(specs=[[{"secondary_y":True}]])
    fig3.add_trace(go.Bar(x=agg_p['Categorie'],y=agg_p['CA_HT'],marker_color=PALETTE[:len(agg_p)],marker_line_width=0,name="CA HT"),secondary_y=False)
    fig3.add_trace(go.Scatter(x=agg_p['Categorie'],y=agg_p['cumul'],mode='lines+markers',name="Cumul %",
        line=dict(color=THEMES['ventes']['accent_lt'],width=2,dash='dot'),marker=dict(size=7,color=THEMES['ventes']['accent_lt'])),secondary_y=True)
    chart_layout(fig3, height=260)
    fig3.update_yaxes(range=[0,110],secondary_y=True,tickfont=dict(color=THEMES['ventes']['accent_lt'],size=9),showgrid=False)
    st.plotly_chart(fig3, width='stretch')

def v_tab_quantites(df):
    kpis([
        ("Qté Totale",   f"{int(df['Qte'].sum()):,}", ACC_V),
        ("Moy / Cmd",    f"{df['Qte'].mean():.1f}",   C['blue']),
        ("Max Commande", f"{int(df['Qte'].max())}",    C['red']),
        ("Commandes",    str(df['Num.CMD'].nunique()),  C['teal']),
    ])

    c1, c2 = st.columns([1, 4])
    with c1: axis = st.radio("Grouper par", ["Produit","Categorie","Type_Vente","Mois","Annee"], key="vq_ax")

    agg = df.groupby(axis)['Qte'].sum().sort_values(ascending=False).reset_index()
    agg[axis] = agg[axis].astype(str)
    total_q = agg['Qte'].sum(); clrs = PALETTE[:len(agg)]

    with c2:
        fig = make_subplots(rows=1,cols=2,specs=[[{"type":"xy"},{"type":"pie"}]])
        fig.add_trace(go.Bar(x=agg[axis],y=agg['Qte'],marker_color=clrs,marker_line_width=0),row=1,col=1)
        fig.add_trace(go.Pie(labels=agg[axis],values=agg['Qte'],marker_colors=clrs,hole=0.4,
            textfont=dict(family="DM Mono",size=9),marker=dict(line=dict(color=C['bg'],width=2))),row=1,col=2)
        chart_layout(fig, height=320, show_legend=False)
        fig.update_xaxes(tickangle=-30, row=1, col=1)
        st.plotly_chart(fig, width='stretch')

    col_t, col_c = st.columns([1, 2])
    with col_t:
        section_hdr("DÉTAIL", accent_color=ACC_V)
        d = agg.copy(); d['Part %'] = (d['Qte']/total_q*100).round(1).astype(str)+"%"; d['Qte'] = d['Qte'].astype(int)
        dark_table(d, height=300)

    with col_c:
        section_hdr("TENDANCE MENSUELLE", accent_color=ACC_V)
        dm = df.copy(); dm['M'] = dm['Date.CMD'].dt.to_period('M').dt.to_timestamp()
        mon = dm.groupby('M')['Qte'].sum().reset_index()
        mon['rolling'] = mon['Qte'].rolling(3, min_periods=1).mean()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=mon['M'],y=mon['Qte'],marker_color=C['blue'],marker_line_width=0,opacity=0.65,name="Quantités"))
        fig2.add_trace(go.Scatter(x=mon['M'],y=mon['rolling'],mode='lines',name="Moy. 3 mois",line=dict(color=ACC_V,width=2.5)))
        chart_layout(fig2, height=300); st.plotly_chart(fig2, width='stretch')


# ══════════════════════════════════════════════════════════════
#  ████  MODULE ACHATS  ████
# ══════════════════════════════════════════════════════════════
ACC_A = THEMES["achats"]["accent"]

def a_tab_overview(df):
    total_ht  = df['Montant_HT'].sum(); total_ttc = df['Montant_TTC'].sum()
    nb_cmd    = df['Num.CMD'].nunique(); nb_four   = df['Fournisseur'].nunique()
    nb_prod   = df['Produit'].nunique(); panier    = total_ht / nb_cmd if nb_cmd else 0

    kpis([
        ("Coût HT Total",  fmt(total_ht),  ACC_A),
        ("Coût TTC Total", fmt(total_ttc), C['ivory_dim']),
        ("Panier Moyen",   fmt(panier),    C['teal']),
        ("Commandes",      str(nb_cmd),    C['blue']),
        ("Fournisseurs",   str(nb_four),   C['green']),
        ("Produits",       str(nb_prod),   C['red']),
    ])

    col1, col2 = st.columns([3, 2])
    with col1:
        section_hdr("ÉVOLUTION MENSUELLE", "Coût HT + Quantités", ACC_A)
        dm = df.copy(); dm['M'] = dm['Date.CMD'].dt.to_period('M').dt.to_timestamp()
        mon = dm.groupby('M').agg(Cout=('Montant_HT','sum'),Qte=('Qte','sum')).reset_index()
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=mon['M'],y=mon['Cout'],name="Coût HT",marker_color=ACC_A,marker_line_width=0,opacity=0.85),secondary_y=False)
        fig.add_trace(go.Scatter(x=mon['M'],y=mon['Qte'],name="Quantités",mode='lines+markers',
            line=dict(color=C['teal'],width=2),marker=dict(size=5,color=C['teal'])),secondary_y=True)
        chart_layout(fig, height=300)
        fig.update_yaxes(tickfont=dict(color=ACC_A,size=9),secondary_y=False,showgrid=True)
        fig.update_yaxes(tickfont=dict(color=C['teal'],size=9),secondary_y=True,showgrid=False)
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(fig, width='stretch')

    with col2:
        section_hdr("PAR CATÉGORIE", "Répartition coûts", ACC_A)
        cat = df.groupby('Categorie')['Montant_HT'].sum().sort_values(ascending=False).reset_index()
        fig2 = go.Figure(go.Pie(labels=cat['Categorie'],values=cat['Montant_HT'],
            marker_colors=PALETTE[:len(cat)],hole=0.55,
            textfont=dict(family="DM Mono",size=10),marker=dict(line=dict(color=C['bg'],width=2))))
        fig2.update_layout(height=300,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(font=dict(family="DM Mono",size=9,color=C['ivory_dim']),bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(text=f"<b>{len(cat)}</b><br>cat.",x=0.5,y=0.5,
                font=dict(family="Bebas Neue",size=22,color=C['ivory']),showarrow=False)])
        st.plotly_chart(fig2, width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        section_hdr("TOP 10 PRODUITS", "par coût HT", ACC_A)
        top10 = df.groupby('Produit')['Montant_HT'].sum().nlargest(10).sort_values().reset_index()
        fig3 = go.Figure(go.Bar(x=top10['Montant_HT'],y=top10['Produit'],orientation='h',
            marker=dict(color=grad_amber(len(top10)),line=dict(width=0)),
            text=[fmt(v) for v in top10['Montant_HT']],textposition='outside',
            textfont=dict(size=9,color=C['text_dim'])))
        chart_layout(fig3, height=320, margin=dict(l=10,r=80,t=10,b=20), show_legend=False)
        fig3.update_xaxes(showgrid=False, showticklabels=False)
        fig3.update_yaxes(tickfont=dict(size=10,color=C['ivory_dim']))
        st.plotly_chart(fig3, width='stretch')

    with col4:
        section_hdr("TOP 10 FOURNISSEURS", "par coût HT", ACC_A)
        top_f = df.groupby('Fournisseur')['Montant_HT'].sum().nlargest(10).sort_values().reset_index()
        fig4 = go.Figure(go.Bar(x=top_f['Montant_HT'],y=top_f['Fournisseur'],orientation='h',
            marker=dict(color=grad_red(len(top_f)),line=dict(width=0)),
            text=[fmt(v) for v in top_f['Montant_HT']],textposition='outside',
            textfont=dict(size=9,color=C['text_dim'])))
        chart_layout(fig4, height=320, margin=dict(l=10,r=80,t=10,b=20), show_legend=False)
        fig4.update_xaxes(showgrid=False, showticklabels=False)
        fig4.update_yaxes(tickfont=dict(size=9,color=C['ivory_dim']))
        st.plotly_chart(fig4, width='stretch')

def a_tab_analyse(df):
    GROUPS  = ["Produit","Categorie","Fournisseur","Type_Achat","Mois","Annee"]
    METRICS = ["Montant_HT","Montant_TTC","Qte"]
    CHARTS  = ["Barres","Barres H","Ligne","Camembert","Treemap"]

    c1,c2,c3,c4,c5 = st.columns([2,2,2,2,1])
    with c1: grp    = st.selectbox("Axe X", GROUPS, key="aa_grp")
    with c2: met    = st.selectbox("Mesure", METRICS, key="aa_met")
    with c3: chtype = st.selectbox("Graphique", CHARTS, key="aa_cht")
    with c4: tri    = st.radio("Tri", ["↓ Desc","↑ Asc"], horizontal=True, key="aa_tri")
    with c5: topn   = st.slider("Top N", 5, 30, 15, key="aa_n")

    agg = df.groupby(grp)[met].sum().sort_values(ascending=(tri=="↑ Asc")).reset_index()
    agg_top = agg.head(topn); total = agg[met].sum(); is_money = "Montant" in met

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    kpis([
        ("Total "+met.replace("_"," "), fmt(total) if is_money else f"{int(total):,}", ACC_A),
        ("Lignes",       str(len(df)),                    C['blue']),
        ("Commandes",    str(df['Num.CMD'].nunique()),     C['teal']),
        ("Fournisseurs", str(df['Fournisseur'].nunique()), C['green']),
    ])

    col_t, col_c = st.columns([1, 2])
    with col_t:
        section_hdr("DONNÉES", f"{grp} / {met}", ACC_A)
        disp = agg_top.copy()
        disp['Part %'] = (disp[met]/total*100).round(1).astype(str)+"%"
        disp[met] = disp[met].apply(fmt) if is_money else disp[met].astype(int)
        dark_table(disp, height=450)
    with col_c:
        section_hdr("VISUALISATION", chtype.upper(), ACC_A)
        xs = agg_top[grp].astype(str); ys = agg_top[met]; clrs = PALETTE[:len(agg_top)]
        fig = _build_chart(chtype, xs, ys, clrs, is_money, ACC_A)
        chart_layout(fig, height=470, show_legend=(chtype=="Camembert"))
        st.plotly_chart(fig, width='stretch')

def a_tab_produits_2024(df):
    df2024 = df[df['Annee'] == 2024].copy()
    kpis([
        ("Produits Distincts", str(df2024['Produit'].nunique()),   ACC_A),
        ("Coût HT Total",      fmt(df2024['Montant_HT'].sum()),    C['green']),
        ("Qté Totale",         f"{int(df2024['Qte'].sum()):,}",    C['blue']),
        ("Commandes",          str(df2024['Num.CMD'].nunique()),    C['teal']),
    ])
    if df2024.empty:
        st.markdown(f'<p style="color:{C["red"]};font-family:DM Mono,monospace;text-align:center;padding:60px">⚠ Aucune donnée pour 2024</p>', unsafe_allow_html=True)
        return

    col1, col2 = st.columns(2)
    with col1:
        section_hdr("STATISTIQUES PRODUITS 2024", accent_color=ACC_A)
        prod = df2024.groupby(['Produit','Categorie']).agg(
            Cout_HT=('Montant_HT','sum'),Qte=('Qte','sum'),Cmds=('Num.CMD','nunique')
        ).reset_index().sort_values('Cout_HT', ascending=False)
        prod['Cout_HT'] = prod['Cout_HT'].apply(fmt)
        prod.columns = ['Produit','Catégorie','Coût HT','Qté','Cmds']
        dark_table(prod, height=360)
    with col2:
        section_hdr("DÉTAIL DES COMMANDES 2024", accent_color=ACC_A)
        det = df2024.sort_values('Date.CMD').copy()
        det = det[['Num.CMD','Date.CMD','Fournisseur','Produit','Qte','Montant_HT']]
        det['Date.CMD']   = det['Date.CMD'].dt.strftime('%d/%m/%Y')
        det['Montant_HT'] = det['Montant_HT'].apply(fmt)
        det.columns = ['N° CMD','Date','Fournisseur','Produit','Qté','Coût HT']
        dark_table(det, height=360)

    section_hdr("RÉPARTITION MENSUELLE 2024", "Coût HT par mois", ACC_A)
    df2024['M'] = df2024['Date.CMD'].dt.to_period('M').dt.to_timestamp()
    mon24 = df2024.groupby('M').agg(Cout=('Montant_HT','sum'),Qte=('Qte','sum')).reset_index()
    fig = make_subplots(rows=1,cols=2,specs=[[{"secondary_y":True},{"type":"pie"}]])
    fig.add_trace(go.Bar(x=mon24['M'],y=mon24['Cout'],name="Coût HT",marker_color=ACC_A,marker_line_width=0,opacity=0.85),row=1,col=1,secondary_y=False)
    fig.add_trace(go.Scatter(x=mon24['M'],y=mon24['Qte'],name="Quantités",mode='lines+markers',
        line=dict(color=C['teal'],width=2),marker=dict(size=5,color=C['teal'])),row=1,col=1,secondary_y=True)
    cat24 = df2024.groupby('Categorie')['Montant_HT'].sum().reset_index()
    fig.add_trace(go.Pie(labels=cat24['Categorie'],values=cat24['Montant_HT'],
        marker_colors=PALETTE[:len(cat24)],hole=0.4,textfont=dict(family="DM Mono",size=10),
        marker=dict(line=dict(color=C['bg'],width=2)),name=""),row=1,col=2)
    chart_layout(fig, height=300); fig.update_xaxes(tickangle=-30, row=1, col=1)
    st.plotly_chart(fig, width='stretch')

def a_tab_quantites(df):
    kpis([
        ("Qté Totale",   f"{int(df['Qte'].sum()):,}", ACC_A),
        ("Moy / Cmd",    f"{df['Qte'].mean():.1f}",   C['blue']),
        ("Max Commande", f"{int(df['Qte'].max())}",    C['red']),
        ("Commandes",    str(df['Num.CMD'].nunique()),  C['teal']),
    ])
    c1, c2 = st.columns([1, 4])
    with c1: axis = st.radio("Grouper par", ["Produit","Categorie","Type_Achat","Mois","Annee"], key="aq_ax")

    agg = df.groupby(axis)['Qte'].sum().sort_values(ascending=False).reset_index()
    agg[axis] = agg[axis].astype(str); total_q = agg['Qte'].sum(); clrs = PALETTE[:len(agg)]

    with c2:
        fig = make_subplots(rows=1,cols=2,specs=[[{"type":"xy"},{"type":"pie"}]])
        fig.add_trace(go.Bar(x=agg[axis],y=agg['Qte'],marker_color=clrs,marker_line_width=0),row=1,col=1)
        fig.add_trace(go.Pie(labels=agg[axis],values=agg['Qte'],marker_colors=clrs,hole=0.4,
            textfont=dict(family="DM Mono",size=9),marker=dict(line=dict(color=C['bg'],width=2))),row=1,col=2)
        chart_layout(fig, height=320, show_legend=False)
        fig.update_xaxes(tickangle=-30, row=1, col=1)
        st.plotly_chart(fig, width='stretch')

    col_t, col_c = st.columns([1, 2])
    with col_t:
        section_hdr("DÉTAIL", accent_color=ACC_A)
        d = agg.copy(); d['Part %']=(d['Qte']/total_q*100).round(1).astype(str)+"%"; d['Qte']=d['Qte'].astype(int)
        dark_table(d, height=300)
    with col_c:
        section_hdr("TENDANCE MENSUELLE", accent_color=ACC_A)
        dm = df.copy(); dm['M'] = dm['Date.CMD'].dt.to_period('M').dt.to_timestamp()
        mon = dm.groupby('M')['Qte'].sum().reset_index()
        mon['rolling'] = mon['Qte'].rolling(3, min_periods=1).mean()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=mon['M'],y=mon['Qte'],marker_color=C['blue'],marker_line_width=0,opacity=0.65,name="Quantités"))
        fig2.add_trace(go.Scatter(x=mon['M'],y=mon['rolling'],mode='lines',name="Moy. 3 mois",line=dict(color=ACC_A,width=2.5)))
        chart_layout(fig2, height=300); st.plotly_chart(fig2, width='stretch')

def a_tab_fournisseurs(df):
    agg = (df.groupby('Fournisseur').agg(
        Cout_Total=('Montant_HT','sum'), Nb_Cmd=('Num.CMD','nunique'), Nb_Produits=('Code_Produit','nunique')
    ).reset_index().sort_values('Cout_Total', ascending=False).reset_index(drop=True))

    cat_four = df.groupby(['Categorie','Fournisseur'])['Montant_HT'].sum().reset_index()
    top_four = (cat_four.loc[cat_four.groupby('Categorie')['Montant_HT'].idxmax()]
                .reset_index(drop=True).sort_values('Montant_HT', ascending=False))

    kpis([
        ("Fournisseurs",    str(len(agg)),               ACC_A),
        ("Coût HT Total",   fmt(agg['Cout_Total'].sum()), C['green']),
        ("Moy/Fournisseur", fmt(agg['Cout_Total'].mean()), C['blue']),
        ("Catégories",      str(df['Categorie'].nunique()), C['teal']),
    ])

    col1, col2 = st.columns([3, 2])
    with col1:
        section_hdr("CLASSEMENT GLOBAL FOURNISSEURS", accent_color=ACC_A)
        d = agg.copy(); d.insert(0,'#',range(1,len(d)+1))
        d['Coût HT'] = d['Cout_Total'].apply(fmt)
        d = d[['#','Fournisseur','Coût HT','Nb_Cmd','Nb_Produits']]
        d.columns = ['#','Fournisseur','Coût HT','Cmds','Produits']
        dark_table(d, height=300)

        section_hdr("TOP FOURNISSEUR PAR CATÉGORIE", accent_color=ACC_A)
        t = top_four.copy(); t['Montant_HT'] = t['Montant_HT'].apply(fmt)
        t.columns = ['Catégorie','Meilleur Fournisseur','Coût HT']
        dark_table(t, height=220)

    with col2:
        section_hdr("PAR FOURNISSEUR", accent_color=ACC_A)
        four_agg = df.groupby('Fournisseur')['Montant_HT'].sum().sort_values(ascending=True).reset_index()
        fig = go.Figure(go.Bar(x=four_agg['Montant_HT'],y=four_agg['Fournisseur'],orientation='h',
            marker=dict(color=grad_amber(len(four_agg)),line=dict(width=0))))
        chart_layout(fig,height=260,margin=dict(l=10,r=60,t=10,b=20),show_legend=False)
        fig.update_xaxes(showgrid=False,showticklabels=False); fig.update_yaxes(tickfont=dict(size=9))
        st.plotly_chart(fig, width='stretch')

        section_hdr("PAR CATÉGORIE", accent_color=ACC_A)
        cat_agg = df.groupby('Categorie')['Montant_HT'].sum().reset_index()
        fig2 = go.Figure(go.Pie(labels=cat_agg['Categorie'],values=cat_agg['Montant_HT'],
            marker_colors=PALETTE[:len(cat_agg)],hole=0.5,textfont=dict(family="DM Mono",size=10),
            marker=dict(line=dict(color=C['bg'],width=2))))
        fig2.update_layout(height=240,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=0,b=0),legend=dict(font=dict(family="DM Mono",size=9,color=C['ivory_dim']),bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig2, width='stretch')

    section_hdr("HEATMAP FOURNISSEUR × CATÉGORIE", "Intensité des coûts", ACC_A)
    pivot = df.pivot_table(values='Montant_HT',index='Fournisseur',columns='Categorie',aggfunc='sum',fill_value=0)
    fig3 = go.Figure(go.Heatmap(z=pivot.values,x=pivot.columns.tolist(),y=pivot.index.tolist(),
        colorscale=[[0,"rgb(28,28,28)"],[0.5,"rgb(150,80,20)"],[1,"rgb(232,168,76)"]],showscale=True,xgap=2,ygap=2))
    chart_layout(fig3,height=max(280,len(pivot)*35),margin=dict(l=10,r=20,t=10,b=40),show_legend=False)
    st.plotly_chart(fig3, width='stretch')

def a_tab_categories(df):
    agg = df.groupby('Categorie').agg(
        Cout_HT=('Montant_HT','sum'), Cout_TTC=('Montant_TTC','sum'),
        Qte=('Qte','sum'), Prods=('Code_Produit','nunique'), Cmds=('Num.CMD','nunique')
    ).reset_index().sort_values('Cout_HT', ascending=False).reset_index(drop=True)
    if agg.empty: st.warning("Aucune donnée."); return

    best = agg.iloc[0]; total = agg['Cout_HT'].sum()
    hero_banner("CATÉGORIE LA PLUS COÛTEUSE", best['Categorie'], [
        ("COÛT HT",       fmt(best['Cout_HT']),              ACC_A),
        ("COÛT TTC",      fmt(best['Cout_TTC']),             C['ivory_dim']),
        ("PART DU TOTAL", f"{best['Cout_HT']/total*100:.1f}%", C['teal']),
        ("QTÉ ACHETÉE",   f"{int(best['Qte']):,}",           C['blue']),
    ], ACC_A)

    col1, col2 = st.columns([1, 2])
    with col1:
        section_hdr("CLASSEMENT", accent_color=ACC_A)
        d = agg.copy(); d.insert(0,'#',[f"#{i+1}" for i in range(len(d))])
        d['Part %']   = (d['Cout_HT']/total*100).round(1).astype(str)+"%"
        d['Coût HT']  = d['Cout_HT'].apply(fmt)
        d['Coût TTC'] = d['Cout_TTC'].apply(fmt)
        d['Qté']      = d['Qte'].astype(int)
        d = d[['#','Categorie','Coût HT','Coût TTC','Part %','Qté','Cmds']]
        d.columns = ['#','Catégorie','Coût HT','Coût TTC','Part %','Qté','Cmds']
        dark_table(d, height=300)

    with col2:
        colors = PALETTE[:len(agg)]
        fig = make_subplots(rows=1,cols=2,specs=[[{"type":"pie"},{"type":"xy"}]])
        fig.add_trace(go.Pie(labels=agg['Categorie'],values=agg['Cout_HT'],marker_colors=colors,hole=0.45,
            pull=[0.06 if i==0 else 0 for i in range(len(agg))],textfont=dict(family="DM Mono",size=10),
            marker=dict(line=dict(color=C['bg'],width=3))),row=1,col=1)
        fig.add_trace(go.Bar(x=agg['Categorie'],y=agg['Cout_HT'],marker_color=colors,marker_line_width=0),row=1,col=2)
        chart_layout(fig,height=300,show_legend=False); fig.update_xaxes(tickangle=-20,row=1,col=2)
        st.plotly_chart(fig, width='stretch')

    section_hdr("ÉVOLUTION MENSUELLE", accent_color=ACC_A)
    dm = df.copy(); dm['M'] = dm['Date.CMD'].dt.to_period('M').dt.to_timestamp()
    cm = dm.groupby(['M','Categorie'])['Montant_HT'].sum().reset_index()
    fig2 = px.area(cm,x='M',y='Montant_HT',color='Categorie',color_discrete_sequence=PALETTE)
    fig2.update_traces(line=dict(width=1.5)); chart_layout(fig2,height=280); st.plotly_chart(fig2,width='stretch')

    section_hdr("ANALYSE PARETO", accent_color=ACC_A)
    agg_p = agg.sort_values('Cout_HT',ascending=False).copy()
    agg_p['cumul'] = agg_p['Cout_HT'].cumsum()/total*100
    fig3 = make_subplots(specs=[[{"secondary_y":True}]])
    fig3.add_trace(go.Bar(x=agg_p['Categorie'],y=agg_p['Cout_HT'],marker_color=PALETTE[:len(agg_p)],marker_line_width=0,name="Coût HT"),secondary_y=False)
    fig3.add_trace(go.Scatter(x=agg_p['Categorie'],y=agg_p['cumul'],mode='lines+markers',name="Cumul %",
        line=dict(color=THEMES['achats']['accent_lt'],width=2,dash='dot'),marker=dict(size=7,color=THEMES['achats']['accent_lt'])),secondary_y=True)
    chart_layout(fig3,height=260)
    fig3.update_yaxes(range=[0,110],secondary_y=True,tickfont=dict(color=THEMES['achats']['accent_lt'],size=9),showgrid=False)
    st.plotly_chart(fig3, width='stretch')


# ══════════════════════════════════════════════════════════════
#  ████  MODULE MARGES  ████
# ══════════════════════════════════════════════════════════════
ACC_M = THEMES["marges"]["accent"]

def m_tab_overview(df):
    v = df[df['type_commande'] == 'VENTE']
    if v.empty: st.warning("Aucune vente dans la sélection."); return

    total_marge = v['MargeTotale'].sum(); total_ca = v['Montant HT'].sum()
    taux_global = total_marge/total_ca if total_ca > 0 else 0
    taux_moy    = v['Taux Marge %'].mean()
    nb_prod     = v['produit'].nunique(); nb_wil = v['Wilaya'].nunique()

    kpis([
        ("Marge Totale",      fmt(total_marge),     ACC_M),
        ("CA Hors Taxes",     fmt(total_ca),        C['ivory_dim']),
        ("Taux Marge Global", fmt_pct(taux_global), C['teal']),
        ("Taux Marge Moy.",   fmt_pct(taux_moy),    C['blue']),
        ("Produits",          str(nb_prod),         C['green']),
        ("Wilayas",           str(nb_wil),          C['red']),
    ])

    col1, col2 = st.columns([3, 2])
    with col1:
        section_hdr("ÉVOLUTION MENSUELLE", "Marge HT + Taux %", ACC_M)
        mon = v.groupby(['Mois','Mois_Nom']).agg(MT=('MargeTotale','sum'),Taux=('Taux Marge %','mean')).reset_index().sort_values('Mois')
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=mon['Mois_Nom'],y=mon['MT'],name="Marge",marker_color=ACC_M,marker_line_width=0,opacity=0.85),secondary_y=False)
        fig.add_trace(go.Scatter(x=mon['Mois_Nom'],y=mon['Taux']*100,name="Taux %",mode='lines+markers',
            line=dict(color=C['teal'],width=2),marker=dict(size=5,color=C['teal'])),secondary_y=True)
        chart_layout(fig,height=300)
        fig.update_yaxes(tickfont=dict(color=ACC_M,size=9),secondary_y=False,showgrid=True)
        fig.update_yaxes(tickfont=dict(color=C['teal'],size=9),secondary_y=True,showgrid=False)
        st.plotly_chart(fig, width='stretch')

    with col2:
        section_hdr("PAR CATÉGORIE", "Répartition Marge", ACC_M)
        cat = v.groupby('Catégorie')['MargeTotale'].sum().sort_values(ascending=False).reset_index()
        fig2 = go.Figure(go.Pie(labels=cat['Catégorie'],values=cat['MargeTotale'],
            marker_colors=PALETTE[:len(cat)],hole=0.55,
            textfont=dict(family="DM Mono",size=10),marker=dict(line=dict(color=C['bg'],width=2))))
        fig2.update_layout(height=300,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(font=dict(family="DM Mono",size=9,color=C['ivory_dim']),bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(text=f"<b>{len(cat)}</b><br>cat.",x=0.5,y=0.5,
                font=dict(family="Bebas Neue",size=22,color=C['ivory']),showarrow=False)])
        st.plotly_chart(fig2, width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        section_hdr("TOP PRODUITS", "par Marge Totale", ACC_M)
        top_p = v.groupby('produit')['MargeTotale'].sum().nlargest(10).sort_values().reset_index()
        fig3 = go.Figure(go.Bar(x=top_p['MargeTotale'],y=top_p['produit'],orientation='h',
            marker=dict(color=grad_teal(len(top_p)),line=dict(width=0)),
            text=[fmt(val) for val in top_p['MargeTotale']],textposition='outside',
            textfont=dict(size=9,color=C['text_dim'])))
        chart_layout(fig3,height=320,margin=dict(l=10,r=90,t=10,b=20),show_legend=False)
        fig3.update_xaxes(showgrid=False,showticklabels=False)
        fig3.update_yaxes(tickfont=dict(size=10,color=C['ivory_dim']))
        st.plotly_chart(fig3, width='stretch')

    with col4:
        section_hdr("TOP WILAYAS", "par Marge Totale", ACC_M)
        top_w = v.groupby('Wilaya')['MargeTotale'].sum().sort_values().reset_index()
        fig4 = go.Figure(go.Bar(x=top_w['MargeTotale'],y=top_w['Wilaya'],orientation='h',
            marker=dict(color=grad_teal(len(top_w)),line=dict(width=0)),
            text=[fmt(val) for val in top_w['MargeTotale']],textposition='outside',
            textfont=dict(size=9,color=C['text_dim'])))
        chart_layout(fig4,height=320,margin=dict(l=10,r=90,t=10,b=20),show_legend=False)
        fig4.update_xaxes(showgrid=False,showticklabels=False)
        fig4.update_yaxes(tickfont=dict(size=9,color=C['ivory_dim']))
        st.plotly_chart(fig4, width='stretch')

def m_tab_analyse(df):
    v = df[df['type_commande'] == 'VENTE']
    if v.empty: st.warning("Aucune vente dans la sélection."); return

    GROUPS  = ["produit","Catégorie","Wilaya","Mois_Nom","Annee","fournisseur"]
    METRICS = ["MargeTotale","MargeUnitaire","Montant HT","Montant TTC","quantité"]
    CHARTS  = ["Barres","Barres H","Ligne","Camembert","Treemap"]

    c1,c2,c3,c4,c5 = st.columns([2,2,2,2,1])
    with c1: grp    = st.selectbox("Axe X", GROUPS, key="ma_grp")
    with c2: met    = st.selectbox("Mesure", METRICS, key="ma_met")
    with c3: chtype = st.selectbox("Graphique", CHARTS, key="ma_cht")
    with c4: tri    = st.radio("Tri", ["↓ Desc","↑ Asc"], horizontal=True, key="ma_tri")
    with c5: topn   = st.slider("Top N", 3, 15, 8, key="ma_n")

    agg = v.groupby(grp)[met].sum().sort_values(ascending=(tri=="↑ Asc")).reset_index()
    agg_top = agg.head(topn); total = agg[met].sum()
    is_money = met in ["MargeTotale","MargeUnitaire","Montant HT","Montant TTC"]

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    kpis([
        ("Total "+met.replace(" ","_"), fmt(total) if is_money else f"{int(total):,}", ACC_M),
        ("Lignes",   str(len(v)),                  C['blue']),
        ("Produits", str(v['produit'].nunique()),   C['teal']),
        ("Wilayas",  str(v['Wilaya'].nunique()),    C['green']),
    ])

    col_t, col_c = st.columns([1, 2])
    with col_t:
        section_hdr("DONNÉES", f"{grp} / {met}", ACC_M)
        disp = agg_top.copy()
        disp['Part %'] = (disp[met]/total*100).round(1).astype(str)+"%" if total else "—"
        disp[met] = disp[met].apply(fmt) if is_money else disp[met].astype(int)
        dark_table(disp, height=450)
    with col_c:
        section_hdr("VISUALISATION", chtype.upper(), ACC_M)
        xs = agg_top[grp].astype(str); ys = agg_top[met]; clrs = PALETTE[:len(agg_top)]
        fig = _build_chart(chtype, xs, ys, clrs, is_money, ACC_M)
        chart_layout(fig, height=470, show_legend=(chtype=="Camembert"))
        st.plotly_chart(fig, width='stretch')

def m_tab_produits(df):
    v = df[df['type_commande'] == 'VENTE']
    if v.empty: st.warning("Aucune vente dans la sélection."); return

    kpis([
        ("Produits",    str(v['produit'].nunique()),       ACC_M),
        ("Marge Totale", fmt(v['MargeTotale'].sum()),      C['green']),
        ("Qté Totale",  f"{int(v['quantité'].sum()):,}",  C['blue']),
        ("Taux Moy.",   fmt_pct(v['Taux Marge %'].mean()), C['teal']),
    ])

    col1, col2 = st.columns(2)
    with col1:
        section_hdr("STATISTIQUES PRODUITS", accent_color=ACC_M)
        prod = v.groupby(['produit','Catégorie']).agg(
            MargeTotale=('MargeTotale','sum'), MargeUnit=('MargeUnitaire','mean'),
            TauxMarge=('Taux Marge %','mean'), Qte=('quantité','sum'),
        ).reset_index().sort_values('MargeTotale', ascending=False)
        prod['MargeTotale'] = prod['MargeTotale'].apply(fmt)
        prod['MargeUnit']   = prod['MargeUnit'].apply(fmt)
        prod['TauxMarge']   = prod['TauxMarge'].apply(fmt_pct)
        prod['Qte']         = prod['Qte'].astype(int)
        prod.columns = ['Produit','Catégorie','Marge Tot.','Marge Unit.','Taux %','Qté']
        dark_table(prod, height=340)
    with col2:
        section_hdr("DERNIÈRES VENTES", "lignes récentes", ACC_M)
        det = v.sort_values('Date_commande', ascending=False).copy()
        det = det[['numero_commande','Date_commande','fournisseur','produit','quantité','MargeTotale','Taux Marge %','Wilaya']]
        det['Date_commande'] = det['Date_commande'].dt.strftime('%d/%m/%Y')
        det['MargeTotale']   = det['MargeTotale'].apply(fmt)
        det['Taux Marge %']  = det['Taux Marge %'].apply(fmt_pct)
        det.columns = ['N° CMD','Date','Client','Produit','Qté','Marge Tot.','Taux %','Wilaya']
        dark_table(det, height=340)

    section_hdr("MARGE vs TAUX", "Scatter par produit", ACC_M)
    bubble = v.groupby('produit').agg(MT=('MargeTotale','sum'),Taux=('Taux Marge %','mean'),Qte=('quantité','sum')).reset_index()
    fig2 = go.Figure(go.Scatter(x=bubble['Taux']*100,y=bubble['MT'],mode='markers+text',
        text=bubble['produit'],textposition='top center',textfont=dict(size=8,color=C['text_dim']),
        marker=dict(size=bubble['Qte'].clip(8,40).tolist(),color=bubble['MT'].tolist(),
            colorscale=[[0,"rgb(33,33,33)"],[1,"rgb(22,160,133)"]],showscale=False,line=dict(width=0),opacity=0.85),
        hovertemplate="<b>%{text}</b><br>Taux: %{x:.1f}%<br>Marge: %{y:,.0f} DA<extra></extra>"))
    chart_layout(fig2,height=320,show_legend=False)
    fig2.update_xaxes(title_text="Taux de Marge (%)",title_font=dict(size=9,color=C['text_dim']))
    fig2.update_yaxes(title_text="Marge Totale (DA)",title_font=dict(size=9,color=C['text_dim']))
    st.plotly_chart(fig2, width='stretch')

def m_tab_wilayas(df):
    v = df[df['type_commande'] == 'VENTE']
    if v.empty: st.warning("Aucune vente dans la sélection."); return

    agg = (v.groupby('Wilaya').agg(MT=('MargeTotale','sum'),Taux=('Taux Marge %','mean'),
        Qte=('quantité','sum'),Prods=('produit','nunique'))
        .reset_index().sort_values('MT',ascending=False).reset_index(drop=True))
    total = agg['MT'].sum()

    kpis([
        ("Wilayas",      str(len(agg)),            ACC_M),
        ("Marge Totale", fmt(total),                C['green']),
        ("Moy/Wilaya",   fmt(agg['MT'].mean()),     C['blue']),
        ("Taux Moy.",    fmt_pct(agg['Taux'].mean()), C['teal']),
    ])

    col1, col2 = st.columns([3, 2])
    with col1:
        section_hdr("CLASSEMENT WILAYAS", accent_color=ACC_M)
        d = agg.copy(); d.insert(0,'#',range(1,len(d)+1))
        d['Part %'] = (d['MT']/total*100).round(1).astype(str)+"%"
        d['Marge']  = d['MT'].apply(fmt); d['Taux'] = d['Taux'].apply(fmt_pct); d['Qte'] = d['Qte'].astype(int)
        d = d[['#','Wilaya','Marge','Taux','Part %','Qte','Prods']]
        d.columns = ['#','Wilaya','Marge Tot.','Taux %','Part %','Qté','Produits']
        dark_table(d, height=480)

    with col2:
        section_hdr("PAR WILAYA", accent_color=ACC_M)
        w = agg.sort_values('MT',ascending=True)
        fig = go.Figure(go.Bar(x=w['MT'],y=w['Wilaya'],orientation='h',
            marker=dict(color=w['MT'].tolist(),colorscale=[[0,"rgb(33,33,33)"],[1,"rgb(22,160,133)"]],showscale=False,line=dict(width=0))))
        chart_layout(fig,height=240,margin=dict(l=10,r=50,t=10,b=20),show_legend=False)
        fig.update_xaxes(showgrid=False,showticklabels=False); fig.update_yaxes(tickfont=dict(size=9))
        st.plotly_chart(fig, width='stretch')

        section_hdr("MARGE PAR CATÉGORIE", accent_color=ACC_M)
        fj = v.groupby('Catégorie')['MargeTotale'].sum().reset_index()
        fig2 = go.Figure(go.Pie(labels=fj['Catégorie'],values=fj['MargeTotale'],
            marker_colors=PALETTE[:len(fj)],hole=0.5,textfont=dict(family="DM Mono",size=10),
            marker=dict(line=dict(color=C['bg'],width=2))))
        fig2.update_layout(height=220,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=0,b=0),legend=dict(font=dict(family="DM Mono",size=9,color=C['ivory_dim']),bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig2, width='stretch')

    section_hdr("HEATMAP WILAYA × CATÉGORIE", "Intensité de la Marge", ACC_M)
    pivot = v.pivot_table(values='MargeTotale',index='Wilaya',columns='Catégorie',aggfunc='sum',fill_value=0)
    fig3 = go.Figure(go.Heatmap(z=pivot.values,x=pivot.columns.tolist(),y=pivot.index.tolist(),
        colorscale=[[0,"rgb(28,28,28)"],[0.5,"rgb(10,100,80)"],[1,"rgb(22,160,133)"]],showscale=True,xgap=2,ygap=2))
    chart_layout(fig3,height=280,margin=dict(l=10,r=20,t=10,b=40),show_legend=False)
    st.plotly_chart(fig3, width='stretch')

def m_tab_categories(df):
    v = df[df['type_commande'] == 'VENTE']
    if v.empty: st.warning("Aucune vente dans la sélection."); return

    agg = v.groupby('Catégorie').agg(
        MT=('MargeTotale','sum'), CA_HT=('Montant HT','sum'),
        Taux=('Taux Marge %','mean'), Qte=('quantité','sum'), Prods=('produit','nunique')
    ).reset_index().sort_values('MT',ascending=False).reset_index(drop=True)
    if agg.empty: st.warning("Aucune donnée."); return

    best = agg.iloc[0]; total = agg['MT'].sum()
    hero_banner("MEILLEURE CATÉGORIE", best['Catégorie'], [
        ("MARGE TOTALE",    fmt(best['MT']),              ACC_M),
        ("PART DE LA MARGE",f"{best['MT']/total*100:.1f}%", C['ivory_dim']),
        ("TAUX DE MARGE",   fmt_pct(best['Taux']),        C['teal']),
        ("QTÉ VENDUE",      str(int(best['Qte'])),        C['blue']),
    ], ACC_M)

    col1, col2 = st.columns([1, 2])
    with col1:
        section_hdr("CLASSEMENT", accent_color=ACC_M)
        d = agg.copy(); d.insert(0,'#',[f"#{i+1}" for i in range(len(d))])
        d['Part %']  = (d['MT']/total*100).round(1).astype(str)+"%"
        d['MT']      = d['MT'].apply(fmt); d['Taux'] = d['Taux'].apply(fmt_pct); d['Qte'] = d['Qte'].astype(int)
        d = d[['#','Catégorie','MT','Taux','Part %','Qte','Prods']]
        d.columns = ['#','Catégorie','Marge Tot.','Taux %','Part %','Qté','Produits']
        dark_table(d, height=300)

    with col2:
        colors = PALETTE[:len(agg)]
        fig = make_subplots(rows=1,cols=2,specs=[[{"type":"pie"},{"type":"xy"}]])
        fig.add_trace(go.Pie(labels=agg['Catégorie'],values=agg['MT'],marker_colors=colors,hole=0.45,
            pull=[0.06 if i==0 else 0 for i in range(len(agg))],textfont=dict(family="DM Mono",size=10),
            marker=dict(line=dict(color=C['bg'],width=3))),row=1,col=1)
        fig.add_trace(go.Bar(x=agg['Catégorie'],y=agg['MT'],marker_color=colors,marker_line_width=0),row=1,col=2)
        chart_layout(fig,height=300,show_legend=False); fig.update_xaxes(tickangle=-20,row=1,col=2)
        st.plotly_chart(fig, width='stretch')

    section_hdr("ÉVOLUTION MENSUELLE", accent_color=ACC_M)
    cm = v.groupby(['Mois_Nom','Mois','Catégorie'])['MargeTotale'].sum().reset_index().sort_values('Mois')
    fig2 = px.area(cm,x='Mois_Nom',y='MargeTotale',color='Catégorie',color_discrete_sequence=PALETTE)
    fig2.update_traces(line=dict(width=1.5)); chart_layout(fig2,height=280); st.plotly_chart(fig2,width='stretch')

    section_hdr("PARETO", accent_color=ACC_M)
    agg_p = agg.sort_values('MT',ascending=False).copy()
    agg_p['cumul'] = agg_p['MT'].cumsum()/total*100
    fig3 = make_subplots(specs=[[{"secondary_y":True}]])
    fig3.add_trace(go.Bar(x=agg_p['Catégorie'],y=agg_p['MT'],marker_color=PALETTE[:len(agg_p)],marker_line_width=0,name="Marge"),secondary_y=False)
    fig3.add_trace(go.Scatter(x=agg_p['Catégorie'],y=agg_p['cumul'],mode='lines+markers',name="Cumul %",
        line=dict(color=THEMES['marges']['accent_lt'],width=2,dash='dot'),marker=dict(size=7,color=THEMES['marges']['accent_lt'])),secondary_y=True)
    chart_layout(fig3,height=260)
    fig3.update_yaxes(range=[0,110],secondary_y=True,tickfont=dict(color=THEMES['marges']['accent_lt'],size=9),showgrid=False)
    st.plotly_chart(fig3, width='stretch')

def m_tab_marges(df):
    v = df[df['type_commande'] == 'VENTE']
    if v.empty: st.warning("Aucune vente dans la sélection."); return

    kpis([
        ("Marge Totale",   fmt(v['MargeTotale'].sum()),       ACC_M),
        ("Marge Unit.Moy", fmt(v['MargeUnitaire'].mean()),    C['blue']),
        ("Taux Max",       fmt_pct(v['Taux Marge %'].max()),  C['red']),
        ("Taux Moy.",      fmt_pct(v['Taux Marge %'].mean()), C['teal']),
    ])

    c1, c2 = st.columns([1, 4])
    with c1: axis = st.radio("Grouper par", ["produit","Catégorie","Wilaya","Mois_Nom","Annee"], key="mm_ax")

    agg = v.groupby(axis)['MargeTotale'].sum().sort_values(ascending=False).reset_index()
    agg[axis] = agg[axis].astype(str); total_m = agg['MargeTotale'].sum(); clrs = PALETTE[:len(agg)]

    with c2:
        fig = make_subplots(rows=1,cols=2,specs=[[{"type":"xy"},{"type":"pie"}]])
        fig.add_trace(go.Bar(x=agg[axis],y=agg['MargeTotale'],marker_color=clrs,marker_line_width=0),row=1,col=1)
        fig.add_trace(go.Pie(labels=agg[axis],values=agg['MargeTotale'],marker_colors=clrs,hole=0.4,
            textfont=dict(family="DM Mono",size=9),marker=dict(line=dict(color=C['bg'],width=2))),row=1,col=2)
        chart_layout(fig,height=320,show_legend=False); fig.update_xaxes(tickangle=-30,row=1,col=1)
        st.plotly_chart(fig, width='stretch')

    col_t, col_c = st.columns([1, 2])
    with col_t:
        section_hdr("DÉTAIL", accent_color=ACC_M)
        d = agg.copy(); d['Part %']=(d['MargeTotale']/total_m*100).round(1).astype(str)+"%"
        d['MargeTotale'] = d['MargeTotale'].apply(fmt)
        dark_table(d, height=300)
    with col_c:
        section_hdr("TENDANCE MENSUELLE", accent_color=ACC_M)
        mon = v.groupby(['Mois','Mois_Nom']).agg(MT=('MargeTotale','sum')).reset_index().sort_values('Mois')
        mon['rolling'] = mon['MT'].rolling(2, min_periods=1).mean()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=mon['Mois_Nom'],y=mon['MT'],marker_color=C['blue'],marker_line_width=0,opacity=0.65,name="Marge"))
        fig2.add_trace(go.Scatter(x=mon['Mois_Nom'],y=mon['rolling'],mode='lines',name="Moy. mobile",line=dict(color=ACC_M,width=2.5)))
        chart_layout(fig2,height=300); st.plotly_chart(fig2,width='stretch')


# ══════════════════════════════════════════════════════════════
#  HELPER: CHART BUILDER (partagé par tous les modules)
# ══════════════════════════════════════════════════════════════
def _build_chart(chtype, xs, ys, clrs, is_money, accent):
    if chtype == "Barres":
        fig = go.Figure(go.Bar(x=xs,y=ys,marker_color=clrs,marker_line_width=0,
            text=[fmt(v) if is_money else str(int(v)) for v in ys],
            textposition='outside',textfont=dict(size=8,color=C['text_dim'])))
        fig.update_xaxes(tickangle=-35)
    elif chtype == "Barres H":
        fig = go.Figure(go.Bar(x=ys,y=xs,orientation='h',marker_color=clrs,marker_line_width=0))
        fig.update_layout(yaxis=dict(autorange="reversed"))
    elif chtype == "Ligne":
        fig = go.Figure(go.Scatter(x=xs,y=ys,mode='lines+markers',
            line=dict(color=accent,width=2.5),
            marker=dict(color=accent,size=7,line=dict(width=0)),
            fill='tozeroy',fillcolor=accent+"14"))
        fig.update_xaxes(tickangle=-35)
    elif chtype == "Camembert":
        fig = go.Figure(go.Pie(labels=xs,values=ys,marker_colors=clrs,hole=0.4,
            textfont=dict(family="DM Mono",size=10),marker=dict(line=dict(color=C['bg'],width=2))))
    elif chtype == "Treemap":
        fig = go.Figure(go.Treemap(labels=xs,values=ys,parents=[""]*len(xs),
            marker_colors=clrs,textfont=dict(family="DM Mono",size=11,color=C['ivory'])))
    return fig


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    module = render_nav()
    th = THEMES[module]
    inject_css(th["accent"], th["accent_lt"])
    render_masthead(module)

    # ── MODULE VENTES ─────────────────────────────────────────
    if module == "ventes":
        if not os.path.exists(CSV_VENTES):
            empty_state("◆", "FICHIER VENTES INTROUVABLE")
            st.markdown(f'<p style="text-align:center;font-family:DM Mono,monospace;font-size:11px;color:{C["text_dim"]};">Attendu : {CSV_VENTES}</p>', unsafe_allow_html=True)
            return
        df_raw = load_ventes()
        filters, date_rng = sidebar_ventes(df_raw)
        df = apply_filters_ventes(df_raw, filters, date_rng)
        if df.empty: no_filter_result(); return

        tabs = st.tabs(["  Overview  ","  Analyse  ","  Produits  ",
                        "  Clients  ","  Catégories  ","  Quantités  "])
        with tabs[0]: v_tab_overview(df)
        with tabs[1]: v_tab_analyse(df)
        with tabs[2]: v_tab_produits(df)
        with tabs[3]: v_tab_clients(df)
        with tabs[4]: v_tab_categories(df)
        with tabs[5]: v_tab_quantites(df)

    # ── MODULE ACHATS ─────────────────────────────────────────
    elif module == "achats":
        if not os.path.exists(CSV_ACHATS):
            empty_state("◈", "FICHIER ACHATS INTROUVABLE")
            st.markdown(f'<p style="text-align:center;font-family:DM Mono,monospace;font-size:11px;color:{C["text_dim"]};">Attendu : {CSV_ACHATS}</p>', unsafe_allow_html=True)
            return
        df_raw = load_achats()
        filters, date_rng = sidebar_achats(df_raw)
        df = apply_filters_achats(df_raw, filters, date_rng)
        if df.empty: no_filter_result(); return

        tabs = st.tabs(["  Overview  ","  Dynamique  ","  Produits 2024  ",
                        "  Quantités  ","  Fournisseurs  ","  Catégories  "])
        with tabs[0]: a_tab_overview(df)
        with tabs[1]: a_tab_analyse(df)
        with tabs[2]: a_tab_produits_2024(df)
        with tabs[3]: a_tab_quantites(df)
        with tabs[4]: a_tab_fournisseurs(df)
        with tabs[5]: a_tab_categories(df)

    # ── MODULE MARGES ─────────────────────────────────────────
    elif module == "marges":
        if not os.path.exists(EXCEL_MARGES):
            empty_state("◇", "FICHIER MARGES INTROUVABLE")
            st.markdown(f'<p style="text-align:center;font-family:DM Mono,monospace;font-size:11px;color:{C["text_dim"]};">Attendu : {EXCEL_MARGES}</p>', unsafe_allow_html=True)
            return
        df_raw = load_marges()
        filters, date_rng = sidebar_marges(df_raw)
        df = apply_filters_marges(df_raw, filters, date_rng)
        if df.empty: no_filter_result(); return

        tabs = st.tabs(["  Overview  ","  Analyse  ","  Produits  ",
                        "  Wilayas  ","  Catégories  ","  Marges  "])
        with tabs[0]: m_tab_overview(df)
        with tabs[1]: m_tab_analyse(df)
        with tabs[2]: m_tab_produits(df)
        with tabs[3]: m_tab_wilayas(df)
        with tabs[4]: m_tab_categories(df)
        with tabs[5]: m_tab_marges(df)


if __name__ == "__main__":
    main()