import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

# Configuração da página com a nova identidade
st.set_page_config(page_title="Audit - Inteligência em Contas Médicas", layout="wide")

# Gerador de Dados Simulado para o MVP
@st.cache_data
def gerar_dados_audit(n=1000):
    np.random.seed(42)
    hospitais = ['Hospital Santa Luzia', 'Centro Clínico Mineiro', 'Hospital de Trauma Regional', 'Clínica Especializada']
    procedimentos = ['Cirurgia Geral', 'Exame de Imagem', 'Consulta Especialista', 'Procedimento Obstétrico']
    data = []
    for i in range(n):
        # Simulando uma taxa de erro de 6%
        is_anomaly = random.random() < 0.06
        valor = np.random.uniform(3000, 5500) if is_anomaly else np.random.normal(700, 120)
        
        data.append({
            'ID Guia': f"TISS-{5000+i}",
            'Prestador': random.choice(hospitais),
            'Serviço': random.choice(procedimentos),
            'Insumo': "Item de Alta Tecnologia" if is_anomaly else "Material Hospitalar Padrão",
            'Valor (R$)': round(valor, 2)
        })
    return pd.DataFrame(data)

# --- SIDEBAR ---
st.sidebar.title("🔍 Audit")
st.sidebar.markdown("### Painel de Controle de Auditoria")
st.sidebar.write("Ajuste os parâmetros da IA para filtrar inconsistências.")

# Slider de sensibilidade estatística
sensibilidade = st.sidebar.slider("Sensibilidade do Filtro (Z-Score)", 1.0, 4.0, 2.5)

st.sidebar.divider()
st.sidebar.markdown("#### Status do Sistema")
st.sidebar.success("Conectado ao Banco de Dados")
st.sidebar.caption("Versão Alpha 1.0")

# --- PROCESSAMENTO ---
df = gerar_dados_audit()
media = df['Valor (R$)'].mean()
std = df['Valor (R$)'].std()
df['Desvio'] = (df['Valor (R$)'] - media) / std
df['Status'] = df['Desvio'].apply(lambda x: "🚩 INCONSISTENTE" if x > sensibilidade else "✅ CONFORME")

# --- INTERFACE PRINCIPAL ---
st.title("Audit: Inteligência de Dados e Compliance")
st.markdown("Análise automatizada de conformidade para operadoras de saúde.")

# Métricas de Alto Nível
total_auditado = df['Valor (R$)'].sum()
total_inconsistente = df[df['Status'] == "🚩 INCONSISTENTE"]['Valor (R$)'].sum()
perc_economia = (total_inconsistente / total_auditado) * 100

m1, m2, m3 = st.columns(3)
m1.metric("Volume Total Processado", f"R$ {total_auditado:,.2f}")
m2.metric("Savings Identificados", f"R$ {total_inconsistente:,.2f}", f"{len(df[df['Status'] == '🚩 INCONSISTENTE'])} itens")
m3.metric("Impacto em Sinistralidade", f"{perc_economia:.2f}%", delta="- Redução", delta_color="normal")

st.divider()

# Visualização de Dados
c1, c2 = st.columns(2)

with c1:
    st.subheader("Anomalias Financeiras por Prestador")
    fig_bar = px.bar(df, x='Prestador', y='Valor (R$)', color='Status', 
                     color_discrete_map={'✅ CONFORME': '#45a049', '🚩 INCONSISTENTE': '#d32f2f'},
                     barmode='group')
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("Dispersão de Custos por Guia")
    fig_scatter = px.scatter(df, x='ID Guia', y='Valor (R$)', color='Status',
                             color_discrete_map={'✅ CONFORME': '#45a049', '🚩 INCONSISTENTE': '#d32f2f'},
                             hover_data=['Insumo'])
    st.plotly_chart(fig_scatter, use_container_width=True)

# Tabela Detalhada com Estilização
st.subheader("Relatório Detalhado de Auditoria")
def highlight_errors(val):
    color = '#ffebed' if val == "🚩 INCONSISTENTE" else 'white'
    return f'background-color: {color}'

st.dataframe(df.style.applymap(highlight_errors, subset=['Status']), use_container_width=True)
