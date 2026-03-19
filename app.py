import streamlit as st
from modules.analise_2024 import page_analyse_2024
from modules.analise_2025 import page_analyse_2025
from modules.analise_2026 import page_analyse_2026
from modules.current_year_analysis import page_current_year
from modules.atualizar_dados import atualizar_banco_de_dados

st.set_page_config(
    page_title="Rentabilidade - Pró-Corpo",
    layout="wide",
    menu_items=None,
)

SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display:ital@0;1&display=swap');

/* ── Fundo e largura ── */
section[data-testid="stSidebar"] {
    background-color: #0e0c12 !important;
    border-right: 1px solid rgba(138, 99, 210, 0.18) !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

/* ── Marca ── */
.sb-brand {
    padding: 22px 20px 16px;
    border-bottom: 1px solid rgba(138, 99, 210, 0.15);
    margin-bottom: 6px;
}
.sb-brand-badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: "DM Sans", sans-serif;
    font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #b48ef0; background: rgba(138, 99, 210, 0.12);
    border: 1px solid rgba(138, 99, 210, 0.25);
    border-radius: 999px; padding: 3px 10px; margin-bottom: 10px;
}
.sb-brand-dot { width: 5px; height: 5px; border-radius: 50%; background: #a070e8; }
.sb-brand-title {
    font-family: "DM Serif Display", Georgia, serif;
    font-size: 1.2rem; font-weight: 400; color: #f0ecfc; line-height: 1.15;
}
.sb-brand-title em { font-style: italic; color: #a070e8; }
.sb-brand-sub { font-family: "DM Sans", sans-serif; font-size: 11px; color: #6b5f84; margin-top: 3px; }

/* ── Labels de seção ── */
.sb-nav-label {
    font-family: "DM Sans", sans-serif;
    font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #6b5f84; padding: 14px 20px 6px;
    display: flex; align-items: center; gap: 8px;
}
.sb-nav-label::after { content: ""; flex: 1; height: 1px; background: rgba(138, 99, 210, 0.15); }

.sb-section-label {
    font-family: "DM Sans", sans-serif;
    font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #6b5f84; padding: 14px 20px 6px;
    display: flex; align-items: center; gap: 8px;
}
.sb-section-label::after { content: ""; flex: 1; height: 1px; background: rgba(138, 99, 210, 0.15); }

/* ── Input de senha ── */
section[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: #1e1829 !important;
    border: 1px solid rgba(138, 99, 210, 0.25) !important;
    border-radius: 10px !important;
    color: #f0ecfc !important;
    font-size: 0.875rem !important;
}
section[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
    border-color: #8a63d2 !important;
    box-shadow: 0 0 0 3px rgba(138, 99, 210, 0.18) !important;
}
section[data-testid="stSidebar"] .stTextInput label { display: none !important; }

/* ── Radio: esconde APENAS o círculo, preserva o texto ── */
section[data-testid="stSidebar"] .stRadio > label {
    display: none !important;
}

/* container de cada opção */
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    display: flex !important;
    align-items: center !important;
    padding: 9px 16px !important;
    border-radius: 10px !important;
    margin: 1px 0 !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
    border-left: 2px solid transparent !important;
}
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background: rgba(138, 99, 210, 0.10) !important;
}
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(138, 99, 210, 0.15) !important;
    border-left: 2px solid #a070e8 !important;
}

/* esconde SOMENTE o widget do círculo (div com role presentation) */
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* texto da opção — sempre visível */
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:last-child p {
    font-family: "DM Sans", sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #b0a0cc !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) > div:last-child p {
    color: #f0ecfc !important;
    font-weight: 600 !important;
}

/* ── Rodapé ── */
.sb-footer {
    padding: 14px 20px;
    border-top: 1px solid rgba(138, 99, 210, 0.12);
    display: flex; align-items: center; gap: 8px;
    margin-top: 16px;
}
.sb-footer-dot {
    width: 6px; height: 6px; border-radius: 50%; background: #4ade80;
}
.sb-footer-text { font-family: "DM Sans", sans-serif; font-size: 11px; color: #6b5f84; }

/* ── Esconde títulos e divisores nativos do Streamlit no sidebar ── */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { display: none !important; }
</style>
"""


def main():
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    # ── Marca ─────────────────────────────────────────────────────────────────
    st.sidebar.markdown("""
    <div class="sb-brand">
        <div class="sb-brand-badge"><div class="sb-brand-dot"></div>Pró-Corpo Estética</div>
        <div class="sb-brand-title"><em>Rentabilidade</em></div>
        <div class="sb-brand-sub">Painel gerencial · Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Senha ─────────────────────────────────────────────────────────────────
    st.sidebar.markdown('<div class="sb-section-label">Acesso</div>', unsafe_allow_html=True)
    password = st.sidebar.text_input("senha", type="password", label_visibility="collapsed")

    if not password:
        st.error("Por favor, insira a senha para acessar o painel.")
        st.stop()

    if password != st.secrets["credentials"]["password"]:
        st.error("Senha incorreta.")
        st.stop()

    # ── Estrutura de menu ─────────────────────────────────────────────────────
    menu_structure = {
        "Análises": {
            "2024":         page_analyse_2024,
            "2025":         page_analyse_2025,
            "2026":         page_analyse_2026,
            "Ano Corrente": page_current_year,
        },
        "Admin": {
            "Atualizar Base de Dados": atualizar_banco_de_dados,
        },
    }

    # ── Categoria ─────────────────────────────────────────────────────────────
    st.sidebar.markdown('<div class="sb-nav-label">Categoria</div>', unsafe_allow_html=True)
    category = st.sidebar.radio(
        "categoria",
        list(menu_structure.keys()),
        label_visibility="collapsed",
        key="category_selector",
    )

    # ── Página ────────────────────────────────────────────────────────────────
    st.sidebar.markdown(f'<div class="sb-nav-label">{category}</div>', unsafe_allow_html=True)
    selected_page = st.sidebar.radio(
        "página",
        list(menu_structure[category].keys()),
        label_visibility="collapsed",
        key="page_selector",
    )

    # ── Rodapé ────────────────────────────────────────────────────────────────
    st.sidebar.markdown("""
    <div class="sb-footer">
        <div class="sb-footer-dot"></div>
        <span class="sb-footer-text">MongoDB Atlas · online</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Renderiza a página ────────────────────────────────────────────────────
    menu_structure[category][selected_page]()


if __name__ == "__main__":
    main()