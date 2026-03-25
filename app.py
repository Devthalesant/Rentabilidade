import streamlit as st
from modules.analise_2024 import page_analyse_2024
from modules.analise_2025 import page_analyse_2025
from modules.analise_2026 import page_analyse_2026
from modules.current_year_analysis import page_current_year
from modules.atualizar_dados import atualizar_banco_de_dados
from Functions.ui import css_sidebar, render_login_screen

st.set_page_config(
    page_title="Rentabilidade - Pró-Corpo",
    layout="wide",
    menu_items=None,
)

def main():
    sidebar_css = css_sidebar()
    st.markdown(sidebar_css, unsafe_allow_html=True)

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
        render_login_screen()
        st.stop()

    if password != st.secrets["credentials"]["password"]:
        render_login_screen(erro=True)
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