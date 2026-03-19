from textwrap import dedent
import streamlit as st
import streamlit.components.v1 as components


# ══════════════════════════════════════════════════════════════════════════════
#  TOKENS GLOBAIS DO TEMA DARK
#  Centralizados aqui para manter consistência entre todas as páginas
# ══════════════════════════════════════════════════════════════════════════════
#
#  Fundo principal  : #0e0c12  (quase preto arroxeado)
#  Superfície card  : #16121f  (um nível acima do fundo)
#  Superfície suave : #1e1829  (cards secundários / inputs)
#  Borda            : rgba(138, 99, 210, 0.20)
#  Roxo neon        : #8a63d2  (acento principal)
#  Roxo vibrante    : #a070e8  (ícones / destaques)
#  Roxo claro       : #c4a8f5  (valores de KPI)
#  Texto primário   : #f0ecfc  (branco levemente lavanda)
#  Texto secundário : #b0a0cc
#  Texto suave      : #6b5f84  (labels, captions)


_CSS_DARK_BASE = dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Serif+Display:ital@0;1&display=swap');

/* ===== Tokens ===== */
:root {
    --dk-bg:            #0e0c12;
    --dk-surface:       #16121f;
    --dk-surface-2:     #1e1829;
    --dk-surface-3:     #241d30;
    --dk-border:        rgba(138, 99, 210, 0.20);
    --dk-border-soft:   rgba(138, 99, 210, 0.12);
    --dk-border-strong: rgba(138, 99, 210, 0.35);

    --dk-purple:        #8a63d2;
    --dk-purple-vivid:  #a070e8;
    --dk-purple-light:  #c4a8f5;
    --dk-purple-neon:   #b48ef0;
    --dk-purple-dim:    rgba(138, 99, 210, 0.15);

    --dk-text:          #f0ecfc;
    --dk-text-mid:      #b0a0cc;
    --dk-text-soft:     #6b5f84;

    --dk-green:         #4ade80;
    --dk-green-bg:      rgba(22, 163, 74, 0.15);
    --dk-red:           #f87171;
    --dk-red-bg:        rgba(220, 38, 38, 0.15);
    --dk-teal:          #2dd4bf;
    --dk-teal-bg:       rgba(13, 148, 136, 0.15);
    --dk-amber:         #fbbf24;
    --dk-amber-bg:      rgba(217, 119, 6, 0.15);

    --dk-shadow-sm:     0 1px 3px rgba(0, 0, 0, 0.4), 0 4px 12px rgba(0, 0, 0, 0.3);
    --dk-shadow-md:     0 2px 8px rgba(0, 0, 0, 0.5), 0 8px 24px rgba(0, 0, 0, 0.4);

    --dk-radius-sm:     10px;
    --dk-radius-md:     16px;
    --dk-radius-lg:     20px;
}

/* ===== Base ===== */
.stApp {
    background-color: var(--dk-bg) !important;
    background-image:
        radial-gradient(ellipse 700px 500px at 95% 0%, rgba(138, 99, 210, 0.07) 0%, transparent 65%),
        radial-gradient(ellipse 500px 400px at 0% 100%, rgba(100, 70, 180, 0.05) 0%, transparent 60%);
}

.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
    padding-left: 4rem !important;
    padding-right: 4rem !important;
    max-width: 1280px !important;
}

/* ===== Tipografia global ===== */
html, body, [class*="css"], .stMarkdown, p, span, div {
    font-family: "DM Sans", "Segoe UI", sans-serif !important;
    color: var(--dk-text);
}

h1, h2, h3 {
    font-family: "DM Serif Display", Georgia, serif !important;
    letter-spacing: -0.01em;
    color: var(--dk-text) !important;
}

.stSubheader {
    font-family: "DM Serif Display", Georgia, serif !important;
    color: var(--dk-purple-light) !important;
}

/* ===== Tabs ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--dk-surface);
    padding: 6px;
    border-radius: var(--dk-radius-lg);
    border: 1px solid var(--dk-border);
    box-shadow: var(--dk-shadow-sm);
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    border-radius: var(--dk-radius-md) !important;
    padding: 0 20px;
    background: transparent;
    color: var(--dk-text-soft);
    font-weight: 500;
    font-size: 0.875rem;
    letter-spacing: 0.01em;
    transition: all 0.18s ease;
    border: none !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--dk-purple-dim);
    color: var(--dk-purple-light);
}

.stTabs [aria-selected="true"] {
    background: var(--dk-purple) !important;
    color: var(--dk-text) !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(138, 99, 210, 0.35) !important;
}

.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ===== Section cards ===== */
.pc-section-card {
    background: var(--dk-surface);
    border: 1px solid var(--dk-border);
    box-shadow: var(--dk-shadow-md);
    border-radius: var(--dk-radius-lg);
    padding: 24px 24px 12px 24px;
    margin-bottom: 1.2rem;
}

/* ===== KPI Cards premium ===== */
.pc-kpi-card {
    background: var(--dk-surface);
    border: 1px solid var(--dk-border);
    border-radius: var(--dk-radius-md);
    padding: 16px 18px 14px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 6px;
    box-shadow: var(--dk-shadow-sm);
}

.pc-kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}

.pc-kpi-card.purple::before { background: linear-gradient(90deg, #7c3aed, #c084fc); }
.pc-kpi-card.teal::before   { background: linear-gradient(90deg, #0d9488, #2dd4bf); }
.pc-kpi-card.red::before    { background: linear-gradient(90deg, #dc2626, #f87171); }
.pc-kpi-card.green::before  { background: linear-gradient(90deg, #16a34a, #4ade80); }
.pc-kpi-card.amber::before  { background: linear-gradient(90deg, #d97706, #fbbf24); }

.pc-kpi-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
}

.pc-kpi-label {
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: var(--dk-text-soft) !important;
}

.pc-kpi-icon {
    width: 30px; height: 30px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}

.pc-kpi-icon.purple { background: rgba(124, 58, 237, 0.18); }
.pc-kpi-icon.teal   { background: rgba(13, 148, 136, 0.18); }
.pc-kpi-icon.red    { background: rgba(220, 38, 38, 0.18);  }
.pc-kpi-icon.green  { background: rgba(22, 163, 74, 0.18);  }
.pc-kpi-icon.amber  { background: rgba(217, 119, 6, 0.18);  }

.pc-kpi-value {
    font-family: "DM Serif Display", Georgia, serif !important;
    font-size: 1.5rem !important;
    font-weight: 400 !important;
    color: var(--dk-text) !important;
    line-height: 1.1 !important;
}

.pc-kpi-delta {
    font-size: 11px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 3px;
    padding: 2px 8px;
    border-radius: 999px;
    width: fit-content;
}

.pc-kpi-delta.up   { color: var(--dk-green); background: var(--dk-green-bg); }
.pc-kpi-delta.down { color: var(--dk-red);   background: var(--dk-red-bg);   }
.pc-kpi-delta.off  { color: var(--dk-text-soft); background: var(--dk-purple-dim); border: 1px solid var(--dk-border); }

/* ===== KPI card secundário ===== */
.pc-kpi-sm {
    background: var(--dk-surface-2);
    border: 1px solid var(--dk-border-soft);
    border-radius: var(--dk-radius-sm);
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.pc-kpi-sm-label {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: var(--dk-text-soft) !important;
}

.pc-kpi-sm-value {
    font-family: "DM Serif Display", Georgia, serif !important;
    font-size: 1.1rem !important;
    color: var(--dk-purple-light) !important;
}

.pc-kpi-sm-sub {
    font-size: 11px !important;
    color: var(--dk-text-soft) !important;
}

/* ===== Section label ===== */
.pc-section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--dk-text-soft);
    margin: 18px 0 10px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.pc-section-label::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--dk-border);
}

/* ===== Botões ===== */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    border-radius: var(--dk-radius-sm) !important;
    border: 1px solid var(--dk-purple) !important;
    padding: 0.6rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.02em !important;
    background: var(--dk-purple) !important;
    color: var(--dk-text) !important;
    box-shadow: 0 2px 12px rgba(138, 99, 210, 0.25) !important;
    transition: all 0.16s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--dk-purple-vivid) !important;
    border-color: var(--dk-purple-vivid) !important;
    box-shadow: 0 4px 20px rgba(138, 99, 210, 0.40) !important;
    transform: translateY(-1px) !important;
}

/* ===== Inputs ===== */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
    border-radius: var(--dk-radius-sm) !important;
    border: 1px solid var(--dk-border) !important;
    background: var(--dk-surface-2) !important;
    color: var(--dk-text) !important;
    font-size: 0.9rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--dk-purple) !important;
    box-shadow: 0 0 0 3px rgba(138, 99, 210, 0.18) !important;
}

.stSelectbox > div > div {
    border-radius: var(--dk-radius-sm) !important;
    border: 1px solid var(--dk-border) !important;
    background: var(--dk-surface-2) !important;
    color: var(--dk-text) !important;
}

.stTextInput label, .stNumberInput label,
.stSelectbox label, .stFileUploader label {
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: var(--dk-text-soft) !important;
}

/* ===== File uploader ===== */
section[data-testid="stFileUploader"] {
    background: var(--dk-surface-2);
    border: 1px dashed var(--dk-border);
    border-radius: var(--dk-radius-md);
    padding: 10px 14px;
    transition: border-color 0.15s ease;
}

section[data-testid="stFileUploader"]:hover {
    border-color: var(--dk-purple);
}

/* ===== Dataframe / editor ===== */
div[data-testid="stDataFrame"],
div[data-testid="stDataEditor"] {
    border-radius: var(--dk-radius-md) !important;
    border: 1px solid var(--dk-border) !important;
    overflow: hidden !important;
    box-shadow: var(--dk-shadow-sm) !important;
}

/* ===== st.metric nativo (fallback) ===== */
div[data-testid="metric-container"] {
    background: var(--dk-surface);
    border: 1px solid var(--dk-border);
    border-radius: var(--dk-radius-md);
    padding: 16px 18px;
    box-shadow: var(--dk-shadow-sm);
    position: relative;
    overflow: hidden;
}

div[data-testid="metric-container"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--dk-purple), var(--dk-purple-light));
}

div[data-testid="metric-container"] label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--dk-text-soft) !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: "DM Serif Display", Georgia, serif !important;
    font-size: 1.3rem !important;
    color: var(--dk-purple-light) !important;
}

/* ===== Alerts ===== */
div[data-baseweb="notification"] {
    border-radius: var(--dk-radius-md) !important;
    border-left: 3px solid var(--dk-purple) !important;
    background: var(--dk-surface) !important;
    font-size: 0.9rem !important;
}

/* ===== Expanders ===== */
details {
    background: var(--dk-surface-2) !important;
    border: 1px solid var(--dk-border) !important;
    border-radius: var(--dk-radius-md) !important;
    padding: 4px 14px !important;
}

details summary {
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--dk-text-mid);
    padding: 10px 0;
}

/* ===== Divider ===== */
hr {
    border: none;
    height: 1px;
    background: var(--dk-border);
    margin: 1.4rem 0;
    opacity: 0.7;
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--dk-purple); border-radius: 99px; }

/* ===== Container com borda (st.container border=True) ===== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--dk-surface-2) !important;
    border: 1px solid var(--dk-border) !important;
    border-radius: var(--dk-radius-md) !important;
}
</style>
""")


# ══════════════════════════════════════════════════════════════════════════════
#  ÍCONES SVG compartilhados
# ══════════════════════════════════════════════════════════════════════════════

_ICONS = {
    "faturamento": ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#a070e8" stroke-width="1.6">'
                    '<polyline points="2,11 6,7 9,10 14,4"/>'
                    '<polyline points="10,4 14,4 14,8"/></svg>'),

    "custo":       ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#f87171" stroke-width="1.6">'
                    '<polyline points="2,5 6,9 9,6 14,12"/>'
                    '<polyline points="10,12 14,12 14,8"/></svg>'),

    "resultado":   ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#4ade80" stroke-width="1.6">'
                    '<circle cx="8" cy="8" r="6"/>'
                    '<polyline points="5.5,8.5 7,10 10.5,6"/></svg>'),

    "margem":      ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#2dd4bf" stroke-width="1.6">'
                    '<circle cx="8" cy="8" r="6"/>'
                    '<line x1="5" y1="11" x2="11" y2="5"/></svg>'),

    "ticket":      ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#fbbf24" stroke-width="1.6">'
                    '<rect x="2" y="4" width="12" height="9" rx="1.5"/>'
                    '<line x1="5" y1="4" x2="5" y2="2.5"/>'
                    '<line x1="11" y1="4" x2="11" y2="2.5"/>'
                    '<line x1="5" y1="9" x2="11" y2="9"/></svg>'),

    "tempo":       ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#2dd4bf" stroke-width="1.6">'
                    '<circle cx="8" cy="8" r="6"/>'
                    '<polyline points="8,5 8,8 10.5,10"/></svg>'),

    "ociosidade":  ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#f87171" stroke-width="1.6">'
                    '<circle cx="8" cy="8" r="6"/>'
                    '<line x1="8" y1="5" x2="8" y2="8.5"/>'
                    '<circle cx="8" cy="10.5" r="0.8" fill="#f87171"/></svg>'),

    "pedidos":     ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#a070e8" stroke-width="1.6">'
                    '<rect x="3" y="2" width="10" height="13" rx="1.5"/>'
                    '<line x1="5.5" y1="6" x2="10.5" y2="6"/>'
                    '<line x1="5.5" y1="9" x2="10.5" y2="9"/>'
                    '<line x1="5.5" y1="12" x2="8" y2="12"/></svg>'),

    "clientes":    ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#fbbf24" stroke-width="1.6">'
                    '<circle cx="8" cy="5.5" r="2.5"/>'
                    '<path d="M2.5,13.5 C2.5,10.5 5,8.5 8,8.5 C11,8.5 13.5,10.5 13.5,13.5"/></svg>'),

    "database":    ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#a070e8" stroke-width="1.6">'
                    '<ellipse cx="8" cy="4" rx="5" ry="2"/>'
                    '<path d="M3,4 v4 c0,1.1 2.24,2 5,2 s5-0.9 5-2 V4"/>'
                    '<path d="M3,8 v4 c0,1.1 2.24,2 5,2 s5-0.9 5-2 V8"/></svg>'),

    "upload":      ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#a070e8" stroke-width="1.6">'
                    '<polyline points="4,6 8,2 12,6"/>'
                    '<line x1="8" y1="2" x2="8" y2="11"/>'
                    '<path d="M2,13 h12"/></svg>'),

    "settings":    ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" '
                    'stroke="#a070e8" stroke-width="1.6">'
                    '<circle cx="8" cy="8" r="2.5"/>'
                    '<path d="M8,1.5 v1.5 M8,13 v1.5 M1.5,8 h1.5 M13,8 h1.5 '
                    'M3.5,3.5 l1,1 M11.5,11.5 l1,1 M11.5,3.5 l-1,1 M3.5,11.5 l1,-1"/></svg>'),
}

_COLOR_MAP = {
    "faturamento": "purple",
    "custo":       "red",
    "resultado":   "green",
    "margem":      "teal",
    "ticket":      "amber",
    "tempo":       "teal",
    "ociosidade":  "red",
    "pedidos":     "purple",
    "clientes":    "amber",
    "database":    "purple",
    "upload":      "purple",
    "settings":    "purple",
}


# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA DE RENTABILIDADE
# ══════════════════════════════════════════════════════════════════════════════

def aplicar_ui_pro_rentabilidade(
    page_title: str = "Análise de <em>Rentabilidade</em>",
    subtitle: str = "Painel gerencial de desempenho e resultado financeiro",
    ano: int = None,
    mes_referencia: str = None,
):
    """
    Aplica o CSS global dark e renderiza o header da página de Rentabilidade.

    Parâmetros
    ----------
    page_title      : Título (suporta <em> para itálico roxo)
    subtitle        : Subtítulo / descrição
    ano             : Ano do período (ex: 2025). Se None, oculta a pílula.
    mes_referencia  : Último mês atualizado (ex: "Mar 2025"). Se None, oculta.
    """
    st.markdown(_CSS_DARK_BASE, unsafe_allow_html=True)

    pills_html = ""
    if ano:
        pills_html += f"""
        <div class="rp-pill">
            <span class="rp-pill-label">Período</span>
            <span class="rp-pill-value">Jan – Dez {ano}</span>
        </div>"""
    if mes_referencia:
        pills_html += f"""
        <div class="rp-pill">
            <span class="rp-pill-label">Atualizado</span>
            <span class="rp-pill-value">{mes_referencia}</span>
        </div>"""

    header_html = dedent(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background: transparent; font-family: "DM Sans", sans-serif; }}

            .rp-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 20px;
                flex-wrap: wrap;
                padding: 22px 28px;
                background: #16121f;
                border: 1px solid rgba(138, 99, 210, 0.25);
                border-top: 3px solid #8a63d2;
                border-radius: 18px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.5), 0 8px 24px rgba(0,0,0,0.4);
            }}

            .rp-left {{ display: flex; flex-direction: column; gap: 5px; }}

            .rp-badge {{
                display: inline-flex; align-items: center; gap: 6px;
                font-size: 11px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase;
                color: #b48ef0; background: rgba(138, 99, 210, 0.12);
                border: 1px solid rgba(138, 99, 210, 0.28);
                border-radius: 999px; padding: 3px 10px; width: fit-content;
            }}
            .rp-dot {{ width: 6px; height: 6px; border-radius: 50%; background: #a070e8; }}

            .rp-title {{
                font-family: "DM Serif Display", Georgia, serif;
                font-size: 1.65rem; font-weight: 400;
                color: #f0ecfc; line-height: 1.1;
            }}
            .rp-title em {{ font-style: italic; color: #a070e8; }}

            .rp-sub {{ font-size: 0.82rem; color: #6b5f84; line-height: 1.5; }}

            .rp-right {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}

            .rp-pill {{
                display: flex; flex-direction: column; align-items: flex-end;
                padding: 8px 14px;
                background: #1e1829;
                border: 1px solid rgba(138, 99, 210, 0.20);
                border-radius: 12px; gap: 2px;
            }}
            .rp-pill-label {{
                font-size: 10px; font-weight: 700; letter-spacing: 0.07em;
                text-transform: uppercase; color: #6b5f84;
            }}
            .rp-pill-value {{
                font-family: "DM Serif Display", Georgia, serif;
                font-size: 1rem; color: #c4a8f5; line-height: 1.1;
            }}
        </style>
    </head>
    <body>
        <div class="rp-header">
            <div class="rp-left">
                <div class="rp-badge"><div class="rp-dot"></div>Pró-Corpo Estética</div>
                <div class="rp-title">{page_title}</div>
                <div class="rp-sub">{subtitle}</div>
            </div>
            <div class="rp-right">{pills_html}</div>
        </div>
    </body>
    </html>
    """)

    components.html(header_html, height=130, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA ADM
# ══════════════════════════════════════════════════════════════════════════════

def aplicar_ui_pro_corpo(
    page_title: str = "Atualizar Banco de Dados",
    subtitle: str = "Gestão centralizada de bases, custos e de-para de procedimentos",
):
    """
    Aplica o CSS global dark e renderiza o header da página Adm (cadastros/uploads).

    Parâmetros
    ----------
    page_title : Título da página
    subtitle   : Subtítulo / descrição
    """
    st.markdown(_CSS_DARK_BASE, unsafe_allow_html=True)

    hero_html = dedent(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background: transparent; font-family: "DM Sans", sans-serif; }}

            .hero {{
                position: relative;
                overflow: hidden;
                padding: 28px 32px 26px;
                border-radius: 18px;
                background: #16121f;
                border: 1px solid rgba(138, 99, 210, 0.25);
                border-top: 3px solid #8a63d2;
                box-shadow: 0 2px 8px rgba(0,0,0,0.5), 0 16px 40px rgba(0,0,0,0.4);
            }}

            .hero::after {{
                content: "";
                position: absolute;
                right: -80px; bottom: -80px;
                width: 280px; height: 280px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(138, 99, 210, 0.07) 0%, transparent 70%);
                pointer-events: none;
            }}

            .hero-inner {{
                position: relative; z-index: 1;
                display: flex; align-items: center;
                justify-content: space-between;
                gap: 24px; flex-wrap: wrap;
            }}

            .hero-left {{ flex: 1; min-width: 260px; }}

            .badge {{
                display: inline-flex; align-items: center; gap: 6px;
                padding: 4px 12px;
                font-size: 11px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase;
                color: #b48ef0; background: rgba(138, 99, 210, 0.12);
                border: 1px solid rgba(138, 99, 210, 0.28);
                border-radius: 999px; margin-bottom: 12px;
            }}
            .badge-dot {{ width: 6px; height: 6px; border-radius: 50%; background: #a070e8; }}

            .title {{
                font-family: "DM Serif Display", Georgia, serif;
                font-size: 1.8rem; line-height: 1.08;
                color: #f0ecfc; margin-bottom: 8px; font-weight: 400;
            }}
            .title em {{ font-style: italic; color: #a070e8; }}

            .subtitle {{
                font-size: 0.88rem; line-height: 1.6;
                color: #6b5f84; font-weight: 400; max-width: 520px;
            }}

            .hero-stats {{
                display: flex; gap: 10px; flex-wrap: wrap; align-items: stretch;
            }}

            .stat {{
                min-width: 110px;
                padding: 13px 16px;
                border-radius: 12px;
                background: #1e1829;
                border: 1px solid rgba(138, 99, 210, 0.18);
                text-align: left;
            }}

            .stat-label {{
                font-size: 10px; font-weight: 700; letter-spacing: 0.07em;
                text-transform: uppercase; color: #6b5f84; margin-bottom: 5px;
            }}

            .stat-value {{
                font-family: "DM Serif Display", Georgia, serif;
                font-size: 1rem; color: #c4a8f5; line-height: 1.1;
            }}

            .stat-sub {{
                font-size: 10px; color: #4a4060; margin-top: 3px;
            }}
        </style>
    </head>
    <body>
        <div class="hero">
            <div class="hero-inner">
                <div class="hero-left">
                    <div class="badge">
                        <div class="badge-dot"></div>
                        Pró-Corpo Estética
                    </div>
                    <div class="title">{page_title}</div>
                    <div class="subtitle">{subtitle}</div>
                </div>
                <div class="hero-stats">
                    <div class="stat">
                        <div class="stat-label">Sistema</div>
                        <div class="stat-value">Rentabilidade</div>
                        <div class="stat-sub">Análise anual</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Ambiente</div>
                        <div class="stat-value">Produção</div>
                        <div class="stat-sub">MongoDB Atlas</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Status</div>
                        <div class="stat-value">Ativo</div>
                        <div class="stat-sub">Banco online</div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

    components.html(hero_html, height=175, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
#  COMPONENTES DE KPI
# ══════════════════════════════════════════════════════════════════════════════

def render_kpi_financeiro(
    label: str,
    valor: str,
    tipo: str = "faturamento",
    delta: str | None = None,
    delta_tipo: str = "off",
    help: str | None = None,
):
    """
    Card de KPI premium com ícone, barra colorida no topo e delta badge.

    Parâmetros
    ----------
    label      : Nome do indicador (ex: "Faturamento Total")
    valor      : Valor já formatado (ex: "R$ 2,4M")
    tipo       : Define cor e ícone. Opções:
                 faturamento | custo | resultado | margem | ticket |
                 tempo | ociosidade | pedidos | clientes | database | upload
    delta      : Texto do delta (ex: "↑ 12,3% vs 2024"). Se None, oculta.
    delta_tipo : "up" (verde) | "down" (vermelho) | "off" (neutro)
    help       : Exibe um st.caption abaixo do card como tooltip textual.
    """
    cor   = _COLOR_MAP.get(tipo, "purple")
    icone = _ICONS.get(tipo, _ICONS["faturamento"])

    delta_html = (
        f'<span class="pc-kpi-delta {delta_tipo}">{delta}</span>'
        if delta else ""
    )

    st.markdown(f"""
    <div class="pc-kpi-card {cor}">
        <div class="pc-kpi-top">
            <span class="pc-kpi-label">{label}</span>
            <div class="pc-kpi-icon {cor}">{icone}</div>
        </div>
        <div class="pc-kpi-value">{valor}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

    if help:
        st.caption(f"ℹ️ {help}")


def render_kpi_operacional(
    label: str,
    valor: str,
    sub: str = "",
    tipo: str = "pedidos",
    delta: str | None = None,
    delta_tipo: str = "off",
):
    """
    Card de KPI secundário (menor, fundo suave) para métricas operacionais.

    Parâmetros
    ----------
    label      : Nome do indicador
    valor      : Valor já formatado
    sub        : Texto auxiliar abaixo do valor (ex: "no período")
    tipo       : Define cor e ícone (mesmas opções de render_kpi_financeiro)
    delta      : Texto do delta. Se None, oculta.
    delta_tipo : "up" | "down" | "off"
    """
    icone = _ICONS.get(tipo, _ICONS["pedidos"])
    cor   = _COLOR_MAP.get(tipo, "purple")

    delta_html = (
        f'<span class="pc-kpi-delta {delta_tipo}" style="margin-top:2px;">{delta}</span>'
        if delta else ""
    )

    sub_html = f'<span class="pc-kpi-sm-sub">{sub}</span>' if sub else ""

    st.markdown(f"""
    <div class="pc-kpi-sm">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
            <span class="pc-kpi-sm-label">{label}</span>
            <div class="pc-kpi-icon {cor}" style="width:26px;height:26px;border-radius:7px;">{icone}</div>
        </div>
        <span class="pc-kpi-sm-value">{valor}</span>
        {sub_html}
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_label(texto: str):
    """Divisor de seção com linha horizontal estilizada."""
    st.markdown(
        f'<div class="pc-section-label">{texto}</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  UTILITÁRIOS GENÉRICOS
# ══════════════════════════════════════════════════════════════════════════════

def abrir_card_ui():
    """Abre um container card estilizado (fechar com fechar_card_ui)."""
    st.markdown('<div class="pc-section-card">', unsafe_allow_html=True)


def fechar_card_ui():
    """Fecha o container card aberto por abrir_card_ui."""
    st.markdown('</div>', unsafe_allow_html=True)