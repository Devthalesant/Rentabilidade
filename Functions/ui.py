from textwrap import dedent
import streamlit as st
import streamlit.components.v1 as components


def aplicar_ui_pro_corpo(
    page_title: str = "Atualizar Banco de Dados",
    subtitle: str = "Gestão centralizada de bases, custos e de-para de procedimentos"
):
    css = dedent("""
    <style>
    /* ===== Base ===== */
    .stApp {
        background: linear-gradient(180deg, #fcfaff 0%, #f7f1ff 45%, #f3ebff 100%);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }

    /* ===== Tipografia ===== */
    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255,255,255,0.72);
        padding: 8px;
        border-radius: 18px;
        border: 1px solid rgba(155, 117, 230, 0.16);
        box-shadow: 0 8px 24px rgba(123, 63, 228, 0.06);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 14px;
        padding: 0 18px;
        background: transparent;
        color: #6f5a8d;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8c52ff 0%, #b785ff 100%) !important;
        color: white !important;
        box-shadow: 0 10px 20px rgba(140, 82, 255, 0.22);
    }

    /* ===== Section cards ===== */
    .pc-section-card {
        background: rgba(255,255,255,0.74);
        border: 1px solid rgba(155, 117, 230, 0.14);
        box-shadow: 0 12px 28px rgba(123, 63, 228, 0.08);
        border-radius: 22px;
        padding: 18px 18px 6px 18px;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }

    /* ===== Botões ===== */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        border-radius: 14px !important;
        border: none !important;
        padding: 0.65rem 1.1rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #8c52ff 0%, #b785ff 100%) !important;
        color: white !important;
        box-shadow: 0 10px 20px rgba(140, 82, 255, 0.20) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(140, 82, 255, 0.28) !important;
        filter: brightness(1.02);
    }

    /* ===== Inputs ===== */
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stSelectbox > div > div,
    .stTextArea textarea {
        border-radius: 14px !important;
        border: 1px solid rgba(155, 117, 230, 0.22) !important;
        background: rgba(255,255,255,0.88) !important;
        box-shadow: 0 4px 14px rgba(123, 63, 228, 0.04);
    }

    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stFileUploader label {
        font-weight: 600 !important;
        color: #5d4b77 !important;
    }

    /* ===== File uploader ===== */
    section[data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.76);
        border: 1px dashed rgba(155, 117, 230, 0.28);
        border-radius: 18px;
        padding: 8px 10px;
    }

    /* ===== Dataframe / editor ===== */
    div[data-testid="stDataFrame"],
    div[data-testid="stDataEditor"] {
        border-radius: 18px !important;
        border: 1px solid rgba(155, 117, 230, 0.16) !important;
        overflow: hidden !important;
        box-shadow: 0 10px 24px rgba(123, 63, 228, 0.06) !important;
        background: rgba(255,255,255,0.82);
    }

    /* ===== Metric ===== */
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(155, 117, 230, 0.14);
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: 0 10px 24px rgba(123, 63, 228, 0.06);
    }

    div[data-testid="metric-container"] label {
        color: #7a6697 !important;
        font-weight: 700 !important;
    }

    /* ===== Alerts ===== */
    div[data-baseweb="notification"] {
        border-radius: 16px !important;
        border: 1px solid rgba(155, 117, 230, 0.12) !important;
    }

    /* ===== Expanders ===== */
    details {
        background: rgba(255,255,255,0.70);
        border: 1px solid rgba(155, 117, 230, 0.14);
        border-radius: 18px;
        padding: 6px 12px;
    }

    /* ===== Divider ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, rgba(140,82,255,0), rgba(140,82,255,0.28), rgba(140,82,255,0));
        margin: 1.3rem 0;
    }
    </style>
    """)

    st.markdown(css, unsafe_allow_html=True)

    hero_html = dedent(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: Inter, "Segoe UI", sans-serif;
            }}

            .pc-hero {{
                position: relative;
                overflow: hidden;
                padding: 28px 30px;
                border-radius: 24px;
                background:
                    radial-gradient(circle at top right, rgba(255,255,255,0.65) 0%, rgba(255,255,255,0) 28%),
                    linear-gradient(135deg, #7b3fe4 0%, #a96cf5 52%, #d4b3ff 100%);
                box-shadow:
                    0 18px 45px rgba(123, 63, 228, 0.18),
                    inset 0 1px 0 rgba(255,255,255,0.25);
                color: white;
            }}

            .pc-hero::after {{
                content: "";
                position: absolute;
                right: -60px;
                top: -60px;
                width: 220px;
                height: 220px;
                background: rgba(255,255,255,0.10);
                border-radius: 50%;
                filter: blur(4px);
            }}

            .pc-badge {{
                display: inline-block;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.04em;
                text-transform: uppercase;
                background: rgba(255,255,255,0.16);
                border: 1px solid rgba(255,255,255,0.22);
                border-radius: 999px;
                margin-bottom: 14px;
                backdrop-filter: blur(8px);
            }}

            .pc-hero-grid {{
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 20px;
                flex-wrap: wrap;
            }}

            .pc-title {{
                font-size: 2.35rem;
                line-height: 1.05;
                font-weight: 800;
                margin: 0 0 10px 0;
                color: white;
            }}

            .pc-subtitle {{
                font-size: 1rem;
                line-height: 1.5;
                opacity: 0.96;
                margin: 0;
                max-width: 740px;
            }}

            .pc-hero-side {{
                min-width: 260px;
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                justify-content: flex-end;
            }}

            .pc-mini-card {{
                min-width: 120px;
                padding: 14px 16px;
                border-radius: 18px;
                background: rgba(255,255,255,0.14);
                border: 1px solid rgba(255,255,255,0.22);
                backdrop-filter: blur(10px);
                box-sizing: border-box;
            }}

            .pc-mini-label {{
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                opacity: 0.9;
                margin-bottom: 6px;
            }}

            .pc-mini-value {{
                font-size: 1rem;
                font-weight: 700;
            }}
        </style>
    </head>
    <body>
        <div class="pc-hero">
            <div class="pc-badge">Pró-Corpo • Painel Administrativo</div>

            <div class="pc-hero-grid">
                <div>
                    <div class="pc-title">{page_title}</div>
                    <div class="pc-subtitle">{subtitle}</div>
                </div>

                <div class="pc-hero-side">
                    <div class="pc-mini-card">
                        <div class="pc-mini-label">Foco</div>
                        <div class="pc-mini-value">Organização</div>
                    </div>

                    <div class="pc-mini-card">
                        <div class="pc-mini-label">Experiência</div>
                        <div class="pc-mini-value">Mais fluida</div>
                    </div>

                    <div class="pc-mini-card">
                        <div class="pc-mini-label">Visual</div>
                        <div class="pc-mini-value">Pró-Corpo</div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

    components.html(hero_html, height=235, scrolling=False)


def abrir_card_ui():
    st.markdown('<div class="pc-section-card">', unsafe_allow_html=True)

def fechar_card_ui():
    st.markdown('</div>', unsafe_allow_html=True)