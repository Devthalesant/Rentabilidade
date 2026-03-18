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