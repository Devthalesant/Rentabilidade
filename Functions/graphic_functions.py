import plotly.graph_objects as go
import streamlit as st 
import pandas as pd

## Função para gerar o gráfico comparativo de faturamento e custo entre os meses atuais e os retroativos (Y-2 max)
def grafico_faturamento_custo_comparativo(lista_de_kpis_retroativos, quadrimestre_selecionado):
        dic_quadrimestre_labels = {
            '1°- QUADRIMESTRE': ['Jan', 'Fev', 'Mar', 'Abr'],
            '2°- QUADRIMESTRE': ['Mai', 'Jun', 'Jul', 'Ago'],
            '3°- QUADRIMESTRE': ['Set', 'Out', 'Nov', 'Dez']
        }

        meses = dic_quadrimestre_labels[quadrimestre_selecionado]
        anos = [serie["name"] for serie in lista_de_kpis_retroativos]

        fig = go.Figure()

        paleta_anos = {
            "2024": "#1f77b4",
            "2025": "#ff2d2d",
            "2026": "#2db7a3"
        }

        paleta_meses = {
            "Jan": "#7f8c8d",
            "Fev": "#9b59b6",
            "Mar": "#27ae60",
            "Abr": "#f39c12",
            "Mai": "#16a085",
            "Jun": "#8e44ad",
            "Jul": "#2ecc71",
            "Ago": "#e67e22",
            "Set": "#2980b9",
            "Out": "#c0392b",
            "Nov": "#d35400",
            "Dez": "#34495e"
        }

        def pegar_valor(lista, indice, default=0):
            return lista[indice] if indice < len(lista) else default

        # Barras = valor líquido
        x_barras = []
        y_barras = []
        textos_barras = []
        cores_barras = []

        for i_mes, mes in enumerate(meses):
            for serie in lista_de_kpis_retroativos:
                ano = serie["name"]
                valor_liquido = pegar_valor(serie["valor_liquido"], i_mes, 0)

                x_label = f"{mes}/{ano}"
                x_barras.append(x_label)
                y_barras.append(valor_liquido)
                textos_barras.append(f'R$ {valor_liquido:,.0f}'.replace(',', '.'))
                cores_barras.append(paleta_anos.get(ano, "#636EFA"))

        fig.add_trace(
            go.Bar(
                name="Valor Líquido",
                x=x_barras,
                y=y_barras,
                text=textos_barras,
                textposition="outside",
                marker_color=cores_barras,
                hovertemplate="Período: %{x}<br>Valor Líquido: R$ %{y:,.0f}<extra></extra>"
            )
        )

        # Linhas = custo do mesmo mês entre anos
        for i_mes, mes in enumerate(meses):
            x_linha = []
            y_linha = []
            textos_linha = []

            for serie in lista_de_kpis_retroativos:
                ano = serie["name"]
                custo = pegar_valor(serie["custo_total"], i_mes, 0)

                x_linha.append(f"{mes}/{ano}")
                y_linha.append(custo)
                textos_linha.append(f'R$ {custo:,.0f}'.replace(',', '.'))

            fig.add_trace(
                go.Scatter(
                    name=f"Custo {mes}",
                    x=x_linha,
                    y=y_linha,
                    mode="lines+markers",
                    line=dict(width=3, color=paleta_meses.get(mes, "#555")),
                    marker=dict(size=8),
                    hovertemplate="Período: %{x}<br>Custo Total: R$ %{y:,.0f}<extra></extra>"
                )
            )

        fig.update_layout(
            title=f"Comparativo de Faturamento e Custo - {quadrimestre_selecionado}",
            xaxis_title="Período",
            yaxis_title="Valor (R$)",
            height=700,
            legend_title="Indicadores",
            bargap=0.25
        )

        return fig

# ── Funções: Gerar Gráficos — Tempo, Taxas e Ociosidade ──────────────────────
# Origem: current_year_analysis.py → SEÇÃO: Tempo, Taxas e Ociosidade
# Colar em: Functions/graphic_functions.py


def grafico_ociosidade_mensal_rede(df_ociosidade_gp: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras empilhadas 100% — Ociosidade vs Tempo Produtivo por mês (nível rede).

    Parâmetros:
        df_ociosidade_gp : DataFrame retornado por tratar_ociosidade_mensal()
                           Colunas esperadas: Mes_str | Produtivo | Ociosidade

    Retorna:
        go.Figure
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_ociosidade_gp["Mes_str"],
        y=df_ociosidade_gp["Produtivo"],
        name="Tempo Produtivo",
        marker_color="#0A84FF",
        text=[f"{v:.0%}" for v in df_ociosidade_gp["Produtivo"]],
        textposition="inside",
        textfont=dict(color="white", size=13, family="Arial Black"),
        insidetextanchor="middle",
    ))

    fig.add_trace(go.Bar(
        x=df_ociosidade_gp["Mes_str"],
        y=df_ociosidade_gp["Ociosidade"],
        name="Ociosidade",
        marker_color="#FF2D55",
        text=[f"{v:.0%}" for v in df_ociosidade_gp["Ociosidade"]],
        textposition="inside",
        textfont=dict(color="white", size=13, family="Arial Black"),
        insidetextanchor="middle",
    ))

    fig.update_layout(
        barmode="stack",
        xaxis_title="Mês",
        yaxis_title="Percentual",
        yaxis_tickformat=".0%",
        yaxis=dict(range=[0, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def grafico_ociosidade_por_unidade(df_graf: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras empilhadas 100% — Ociosidade vs Produtivo para uma unidade específica.

    Parâmetros:
        df_graf : DataFrame retornado por tratar_ociosidade_por_unidade()["df_graf"]
                  Colunas esperadas: mes_label | pct_prod | pct_ocs

    Retorna:
        go.Figure
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_graf["mes_label"],
        y=df_graf["pct_prod"],
        name="Tempo Produtivo",
        marker_color="#00C2FF",
        text=[f"{v:.0%}" for v in df_graf["pct_prod"]],
        textposition="inside",
        textfont=dict(color="white", size=13, family="Arial Black"),
        insidetextanchor="middle",
    ))

    fig.add_trace(go.Bar(
        x=df_graf["mes_label"],
        y=df_graf["pct_ocs"],
        name="Ociosidade",
        marker_color="#FF2D55",
        text=[f"{v:.0%}" for v in df_graf["pct_ocs"]],
        textposition="inside",
        textfont=dict(color="white", size=13, family="Arial Black"),
        insidetextanchor="middle",
    ))

    fig.update_layout(
        barmode="stack",
        yaxis=dict(tickformat=".0%", range=[0, 1]),
        xaxis_title="Mês",
        yaxis_title="",
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF"),
        margin=dict(t=10, b=60),
        height=380,
    )

    return fig


def grafico_custo_fixo_por_minuto(df_graf: pd.DataFrame) -> go.Figure:
    """
    Gráfico de linhas — Evolução do Custo Fixo por Minuto para uma unidade específica.

    Parâmetros:
        df_graf : DataFrame retornado por tratar_ociosidade_por_unidade()["df_graf"]
                  Colunas esperadas: mes_label | custo_total_min | Taxa Sala (Min) | Taxa Ociosidade (Min)

    Retorna:
        go.Figure
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_graf["mes_label"],
        y=df_graf["custo_total_min"],
        mode="lines+markers+text",
        name="Custo Total / Min",
        line=dict(color="#00C2FF", width=3),
        marker=dict(size=8, color="#00C2FF"),
        text=[f"R${v:.4f}" for v in df_graf["custo_total_min"]],
        textposition="top center",
        textfont=dict(color="#00C2FF", size=11),
    ))

    fig.add_trace(go.Scatter(
        x=df_graf["mes_label"],
        y=df_graf["Taxa Sala (Min)"],
        mode="lines+markers+text",
        name="Taxa Sala / Min",
        line=dict(color="#FFD60A", width=2, dash="dash"),
        marker=dict(size=6, color="#FFD60A"),
        text=[f"R${v:.4f}" for v in df_graf["Taxa Sala (Min)"]],
        textposition="top center",
        textfont=dict(color="#FFD60A", size=11),
    ))

    fig.add_trace(go.Scatter(
        x=df_graf["mes_label"],
        y=df_graf["Taxa Ociosidade (Min)"],
        mode="lines+markers+text",
        name="Custo Ocioso / Min",
        line=dict(color="#FF2D55", width=2, dash="dot"),
        marker=dict(size=6, color="#FF2D55"),
        text=[f"R${v:.4f}" for v in df_graf["Taxa Ociosidade (Min)"]],
        textposition="bottom center",
        textfont=dict(color="#FF2D55", size=11),
    ))

    fig.update_layout(
        xaxis_title="Mês",
        yaxis_title="R$ / Min",
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF"),
        margin=dict(t=10, b=60),
        height=380,
    )

    return fig
