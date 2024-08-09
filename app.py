import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Função para carregar dados do arquivo Excel
def carregar_dados_excel(arquivo):
    try:
        df = pd.read_excel(arquivo)
        df.columns = df.columns.str.strip()  # Remove espaços em branco no início e fim dos nomes das colunas
        st.write("Colunas encontradas:", df.columns.tolist())  # Mostrar as colunas carregadas para depuração
        return df
    except Exception as e:
        st.sidebar.error(f'Erro ao carregar dados do arquivo: {e}')
        return pd.DataFrame(columns=["DATA", "LOCALIZAÇÃO", "Status", "Status_chuva"])

# Inputs para adicionar novos dados
st.sidebar.title('Importar Arquivo Excel')

# Input para o upload do arquivo Excel
arquivo_excel = st.sidebar.file_uploader("Escolha um arquivo Excel", type=['xlsx', 'xls'])

if arquivo_excel:
    df_base = carregar_dados_excel(arquivo_excel)
    
    # Verificando se as colunas necessárias existem
    colunas_necessarias = ['DATA', 'LOCALIZAÇÃO', 'Status', 'Status_chuva']
    if all(coluna in df_base.columns for coluna in colunas_necessarias):
        # Transformando a coluna 'DATA' para o formato de data
        df_base['DATA'] = pd.to_datetime(df_base['DATA'], errors='coerce')

        # Removendo linhas onde a data não pôde ser convertida
        df_base = df_base.dropna(subset=['DATA'])

        # Mostrando os dados carregados para depuração
        st.write("Dados carregados do arquivo Excel:")
        #st.write(df_base)

        # Configuração da sidebar para filtros
        st.sidebar.title('Configurações de Filtros')

        # Filtros na sidebar
        status_filtrado = st.sidebar.multiselect("Filtrar por Status", options=df_base['Status'].unique(), default=df_base['Status'].unique())
        status_chuva_filtrado = st.sidebar.multiselect("Filtrar por Status Chuva", options=df_base['Status_chuva'].unique(), default=df_base['Status_chuva'].unique())

        # Filtrando o DataFrame
        df_filtrado = df_base[(df_base['Status'].isin(status_filtrado)) & (df_base['Status_chuva'].isin(status_chuva_filtrado))]

        # Criando o gráfico
        fig = go.Figure()

        # Adicionando quadrados para o status da chuva
        for status_chuva in df_filtrado['Status_chuva'].unique():
            df_chuva = df_filtrado[df_filtrado['Status_chuva'] == status_chuva]
            fig.add_trace(go.Scatter(
                x=df_chuva['DATA'],
                y=df_chuva['LOCALIZAÇÃO'],
                mode='markers',
                marker=dict(
                    size=40,
                    symbol='square',
                    color=(
                        "#FFFFFF" if status_chuva == "Seco" else 
                        "#ADD8E6" if status_chuva == "Intermediário" else 
                        "#0000FF"
                    ),
                    opacity=0.5
                ),
                showlegend=False
            ))

        # Adicionando linhas de status
        for status in df_filtrado['Status'].unique():
            df_status = df_filtrado[df_filtrado['Status'] == status]
            fig.add_trace(go.Scatter(
                x=df_status['DATA'],
                y=df_status['LOCALIZAÇÃO'],
                mode='lines+markers',
                marker=dict(size=10),
                name=status,
                line=dict(width=2)
            ))

        # Ajustando o layout para aceitar texto no eixo Y
        fig.update_layout(
            title='Gráfico de Execução de Obras',
            xaxis_title='Data',
            yaxis_title='Km',
            yaxis=dict(type='category'),
            showlegend=True,
        )

        # Exibindo o gráfico na página principal
        st.plotly_chart(fig)

        # Exibindo a tabela com os dados abaixo do gráfico
        st.subheader('Tabela de Dados')
        st.table(df_filtrado)
    else:
        st.error("O arquivo Excel não contém todas as colunas necessárias: 'DATA', 'LOCALIZAÇÃO', 'Status', 'Status_chuva'.")
else:
    st.write("Por favor, faça o upload de um arquivo Excel para gerar o gráfico.")
