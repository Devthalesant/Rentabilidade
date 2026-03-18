from textwrap import dedent
import streamlit as st
import streamlit.components.v1 as components


def aplicar_ui_pro_corpo(
    page_title: str = "Atualizar Banco de Dados",
    subtitle: str = "Gestão centralizada de bases, custos e de-para de procedimentos"
):
    css = dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Serif+Display:ital@0;1&display=swap');

    /* ===== Tokens ===== */
    :root {
        --pc-bg:           #f8f6f2;
        --pc-surface:      #ffffff;
        --pc-surface-2:    #faf9f7;
        --pc-border:       #e8e2f0;
        --pc-border-soft:  rgba(180, 160, 210, 0.18);

        --pc-lavender:     #b49fd4;
        --pc-lavender-mid: #9b7ec8;
        --pc-plum:         #6b4fa0;
        --pc-plum-dark:    #4e3575;
        --pc-accent:       #c9b8e8;

        --pc-text:         #2d2438;
        --pc-text-mid:     #5c4f72;
        --pc-text-soft:    #9688aa;

        --pc-shadow-sm:    0 1px 3px rgba(80, 50, 120, 0.06), 0 4px 12px rgba(80, 50, 120, 0.04);
        --pc-shadow-md:    0 2px 8px rgba(80, 50, 120, 0.07), 0 8px 24px rgba(80, 50, 120, 0.06);
        --pc-shadow-lg:    0 4px 16px rgba(80, 50, 120, 0.08), 0 16px 40px rgba(80, 50, 120, 0.07);

        --pc-radius-sm:    10px;
        --pc-radius-md:    16px;
        --pc-radius-lg:    22px;
    }

    /* ===== Base ===== */
    .stApp {
        background-color: var(--pc-bg) !important;
        background-image:
            radial-gradient(ellipse 800px 600px at 90% 0%, rgba(185, 160, 230, 0.10) 0%, transparent 65%),
            radial-gradient(ellipse 600px 400px at 0% 100%, rgba(160, 130, 210, 0.07) 0%, transparent 60%);
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 1260px !important;
    }

    /* ===== Tipografia global ===== */
    html, body, [class*="css"], .stMarkdown, p, span, div {
        font-family: "DM Sans", "Segoe UI", sans-serif !important;
        color: var(--pc-text);
    }

    h1, h2, h3 {
        font-family: "DM Serif Display", Georgia, serif !important;
        letter-spacing: -0.01em;
        color: var(--pc-text) !important;
    }

    /* subheader e caption nativos do streamlit */
    .stSubheader {
        font-family: "DM Serif Display", Georgia, serif !important;
        color: var(--pc-plum) !important;
    }

    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: var(--pc-surface);
        padding: 6px;
        border-radius: var(--pc-radius-lg);
        border: 1px solid var(--pc-border);
        box-shadow: var(--pc-shadow-sm);
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: var(--pc-radius-md) !important;
        padding: 0 20px;
        background: transparent;
        color: var(--pc-text-mid);
        font-weight: 500;
        font-size: 0.875rem;
        letter-spacing: 0.01em;
        transition: all 0.18s ease;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(180, 159, 212, 0.10);
        color: var(--pc-plum);
    }

    .stTabs [aria-selected="true"] {
        background: var(--pc-plum) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(107, 79, 160, 0.28) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* ===== Section cards ===== */
    .pc-section-card {
        background: var(--pc-surface);
        border: 1px solid var(--pc-border);
        box-shadow: var(--pc-shadow-md);
        border-radius: var(--pc-radius-lg);
        padding: 24px 24px 12px 24px;
        margin-bottom: 1.2rem;
    }

    /* ===== Botões ===== */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        border-radius: var(--pc-radius-sm) !important;
        border: 1.5px solid var(--pc-plum) !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        letter-spacing: 0.02em !important;
        background: var(--pc-plum) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(107, 79, 160, 0.20) !important;
        transition: all 0.16s ease !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: var(--pc-plum-dark) !important;
        border-color: var(--pc-plum-dark) !important;
        box-shadow: 0 4px 16px rgba(107, 79, 160, 0.30) !important;
        transform: translateY(-1px) !important;
    }

    /* ===== Inputs ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea {
        border-radius: var(--pc-radius-sm) !important;
        border: 1.5px solid var(--pc-border) !important;
        background: var(--pc-surface-2) !important;
        color: var(--pc-text) !important;
        font-size: 0.9rem !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: var(--pc-lavender-mid) !important;
        box-shadow: 0 0 0 3px rgba(155, 126, 200, 0.12) !important;
    }

    .stSelectbox > div > div {
        border-radius: var(--pc-radius-sm) !important;
        border: 1.5px solid var(--pc-border) !important;
        background: var(--pc-surface-2) !important;
    }

    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stFileUploader label {
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: var(--pc-text-mid) !important;
    }

    /* ===== File uploader ===== */
    section[data-testid="stFileUploader"] {
        background: var(--pc-surface-2);
        border: 1.5px dashed var(--pc-border);
        border-radius: var(--pc-radius-md);
        padding: 10px 14px;
        transition: border-color 0.15s ease;
    }

    section[data-testid="stFileUploader"]:hover {
        border-color: var(--pc-lavender-mid);
    }

    /* ===== Dataframe / editor ===== */
    div[data-testid="stDataFrame"],
    div[data-testid="stDataEditor"] {
        border-radius: var(--pc-radius-md) !important;
        border: 1px solid var(--pc-border) !important;
        overflow: hidden !important;
        box-shadow: var(--pc-shadow-sm) !important;
    }

    /* ===== Metric ===== */
    div[data-testid="metric-container"] {
        background: var(--pc-surface);
        border: 1px solid var(--pc-border);
        border-radius: var(--pc-radius-md);
        padding: 16px 18px;
        box-shadow: var(--pc-shadow-sm);
        position: relative;
        overflow: hidden;
    }

    div[data-testid="metric-container"]::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--pc-lavender-mid), var(--pc-accent));
    }

    div[data-testid="metric-container"] label {
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: var(--pc-text-soft) !important;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: "DM Serif Display", Georgia, serif !important;
        font-size: 1.3rem !important;
        color: var(--pc-plum) !important;
    }

    /* ===== Alerts ===== */
    div[data-baseweb="notification"] {
        border-radius: var(--pc-radius-md) !important;
        border-left: 3px solid var(--pc-lavender-mid) !important;
        font-size: 0.9rem !important;
    }

    /* ===== Expanders ===== */
    details {
        background: var(--pc-surface-2);
        border: 1px solid var(--pc-border) !important;
        border-radius: var(--pc-radius-md) !important;
        padding: 4px 14px !important;
    }

    details summary {
        font-weight: 600;
        font-size: 0.875rem;
        color: var(--pc-text-mid);
        padding: 10px 0;
    }

    /* ===== Divider ===== */
    hr {
        border: none;
        height: 1px;
        background: var(--pc-border);
        margin: 1.4rem 0;
        opacity: 0.7;
    }

    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--pc-accent); border-radius: 99px; }
    </style>
    """)

    st.markdown(css, unsafe_allow_html=True)

    hero_html = dedent(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}

            body {{
                background: transparent;
                font-family: "DM Sans", sans-serif;
            }}

            .hero {{
                position: relative;
                overflow: hidden;
                padding: 30px 32px 28px;
                border-radius: 20px;
                background: #ffffff;
                border: 1px solid #e8e2f0;
                box-shadow:
                    0 2px 8px rgba(80, 50, 120, 0.06),
                    0 16px 40px rgba(80, 50, 120, 0.07);
            }}

            /* linha decorativa topo */
            .hero::before {{
                content: "";
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 3px;
                background: linear-gradient(90deg, #6b4fa0 0%, #b49fd4 50%, #e8e2f0 100%);
            }}

            /* forma decorativa fundo */
            .hero::after {{
                content: "";
                position: absolute;
                right: -80px;
                bottom: -80px;
                width: 280px;
                height: 280px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(196, 175, 230, 0.12) 0%, transparent 70%);
                pointer-events: none;
            }}

            .hero-inner {{
                position: relative;
                z-index: 1;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 24px;
                flex-wrap: wrap;
            }}

            .hero-left {{
                flex: 1;
                min-width: 260px;
            }}

            .badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.07em;
                text-transform: uppercase;
                color: #6b4fa0;
                background: rgba(107, 79, 160, 0.07);
                border: 1px solid rgba(107, 79, 160, 0.16);
                border-radius: 999px;
                margin-bottom: 14px;
            }}

            .badge-dot {{
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #6b4fa0;
            }}

            .title {{
                font-family: "DM Serif Display", Georgia, serif;
                font-size: 2rem;
                line-height: 1.08;
                color: #2d2438;
                margin-bottom: 8px;
                font-weight: 400;
            }}

            .title em {{
                font-style: italic;
                color: #6b4fa0;
            }}

            .subtitle {{
                font-size: 0.9rem;
                line-height: 1.6;
                color: #7a6b8a;
                font-weight: 400;
                max-width: 560px;
            }}

            /* Stats à direita */
            .hero-stats {{
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                align-items: stretch;
            }}

            .stat {{
                min-width: 110px;
                padding: 14px 18px;
                border-radius: 14px;
                background: #faf9f7;
                border: 1px solid #e8e2f0;
                text-align: left;
            }}

            .stat-label {{
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.07em;
                text-transform: uppercase;
                color: #9688aa;
                margin-bottom: 6px;
            }}

            .stat-value {{
                font-family: "DM Serif Display", Georgia, serif;
                font-size: 1.1rem;
                color: #4e3575;
                line-height: 1.1;
            }}

            .stat-sub {{
                font-size: 10px;
                color: #b0a0c0;
                margin-top: 3px;
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

    components.html(hero_html, height=180, scrolling=False)


def abrir_card_ui():
    st.markdown('<div class="pc-section-card">', unsafe_allow_html=True)

def fechar_card_ui():
    st.markdown('</div>', unsafe_allow_html=True)