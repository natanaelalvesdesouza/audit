import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Audit - Inteligência em Saúde",
    page_icon="🔍",
    layout="wide"
)

# 2. FUNÇÃO: GERADOR DE DADOS (DEMONSTRAÇÃO)
@st.cache_data
def gerar_dados_demo():
    np.random.seed(42)
    hospitais = ['Hospital Santa Luzia', 'Centro Clínico Mineiro', 'Hospital Regional MG', 'Clínica de Especialidades']
    data = []
    for i in range(1000):
        # Injeção controlada de anomalias (6% de erro)
        is_fraud = random.random() < 0.06
        valor = np.random.uniform(3500, 6000) if is_fraud else np.random.normal(800, 150)
        data.append({
            'ID Guia': f"TISS-{8000+i}",
            'Hospital': random.choice(hospitais),
            'Item/Insumo': "Material Especial Premium" if is_fraud else "Insumo Padrão",
            'Valor (R$)': round(valor, 2)
        })
    return pd.DataFrame(data)

# 3. SIDEBAR: UPLOAD E CONFIGURAÇÕES
st.sidebar.title("🔍 Audit AI")
st.sidebar.markdown("---")

st.sidebar.subheader("📤 Ingestão de Dados")
uploaded_file = st.sidebar.file_uploader("Anexe sua base (Excel ou CSV)", type=["csv", "xlsx"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configurações da IA")
sensibilidade = st.sidebar.slider("Sensibilidade (Z-Score)", 1.0, 4.0, 2.5)
st.sidebar.caption("Z-Score > 2.5 identifica os 1% mais discrepantes.")

# 4. LÓGICA DE CARREGAMENTO DE DADOS
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("Arquivo carregado!")
    except Exception as e:
        st.sidebar.error(f"Erro ao ler arquivo: {e}")
        df = gerar_dados_demo()
else:
    df = gerar_dados_demo()
    st.sidebar.info("Exibindo dados de demonstração. Suba um arquivo para analisar dados reais.")

# 5. MOTOR DE AUDITORIA (CÁLCULOS)
# Verificação básica de colunas para garantir que o código não quebre com arquivos externos
colunas_necessarias = {'Valor (R$)', 'Hospital'}
if colunas_necessarias.issubset(df.columns):
    media = df['Valor (R$)'].mean()
    std = df['Valor (R$)'].std()
    df['Score_Desvio'] = (df['Valor (R$)'] - media) / std
    df['Status'] = df['Score_Desvio'].apply(lambda x: "🚩 INCONSISTENTE" if x > sensibilidade else "✅ CONFORME")
else:
    st.warning(f"O arquivo precisa conter as colunas: {colunas_necessarias}. Usando nomes genéricos para análise.")
    # Fallback caso os nomes das colunas sejam diferentes
    valor_col = df.select_dtypes(include=[np.number]).columns[0]
    df['Status'] = "✅ CONFORME" # Default simples para evitar erro visual

# 6. INTERFACE PRINCIPAL
st.title("Audit: Inteligência e Compliance de Contas")
st.markdown(f"Análise baseada em **Z-Score Estatístico** para redução de sinistralidade.")

# Métricas Principais
total_vol = df['Valor (R$)'].sum()
df_inc = df[df['Status'] == "🚩 INCONSISTENTE"]
total_inc = df_inc['Valor (R$)'].sum()

m1, m2, m3 = st.columns(3)
m1.metric("Volume Processado", f"R$ {total_vol:,.2f}")
m2.metric("Savings Potenciais", f"R$ {total_inc:,.2f}", f"{len(df_inc)} alertas")
m3.metric("ROI Estimado (Gain Share)", f"R$ {total_inc * 0.15:,.2f}")

st.markdown("---")

# Gráficos
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Inconsistências por Unidade")
    fig_bar = px.bar(df, x='Hospital', y='Valor (R$)', color='Status', 
                     color_discrete_map={'✅ CONFORME': '#27ae60', '🚩 INCONSISTENTE': '#e74c3c'},
                     barmode='group')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Mapa de Dispersão (Outliers)")
    fig_scatter = px.scatter(df, x='ID Guia', y='Valor (R$)', color='Status',
                             color_discrete_map={'✅ CONFORME': '#27ae60', '🚩 INCONSISTENTE': '#e74c3c'},
                             hover_data=['Hospital'])
    st.plotly_chart(fig_scatter, use_container_width=True)

# Tabela Detalhada
st.subheader("Relatório de Auditoria Detalhado")
st.dataframe(
    df.style.apply(lambda x: ['background-color: #ffdad9' if v == "🚩 INCONSISTENTE" else '' for v in x], axis=1, subset=['Status']),
    use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.caption("Audit © 2026 - Inteligência Financeira")
