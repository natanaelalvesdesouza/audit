import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Audit | Inteligência em Auditoria",
    page_icon="🛡️",
    layout="wide"
)

def main():
    st.title("🛡️ Audit")
    st.subheader("Plataforma de Inteligência e Detecção de Inconsistências")

    # --- SIDEBAR ---
    st.sidebar.header("Configurações")
    
    # Upload de arquivo
    uploaded_file = st.sidebar.file_uploader("Anexe seu banco de dados (CSV ou Excel)", type=["csv", "xlsx"])
    
    z_threshold = st.sidebar.slider(
        "Rigor da Auditoria (Z-Score)",
        min_value=1.0,
        max_value=4.0,
        value=2.5,
        step=0.1,
        help="Define o limite estatístico para considerar uma guia inconsistente."
    )

    # Cálculo da porcentagem teórica
    prob_teorica = stats.norm.sf(z_threshold) * 100
    st.sidebar.info(f"Filtro atual: Top {prob_teorica:.2f}% de inconsistências.")

    # --- CARREGAMENTO DE DADOS ---
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("Arquivo carregado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return
    else:
        # Dados de exemplo caso nenhum arquivo seja anexado
        st.warning("Aguardando upload de dados. Usando base de exemplo abaixo...")
        np.random.seed(42)
        n = 500
        df = pd.DataFrame({
            'ID_Guia': [f"G-{i:05d}" for i in range(n)],
            'Valor_R$': np.random.lognormal(6, 0.8, n),
            'Prestador': np.random.choice(['Clínica A', 'Hospital B', 'Laboratório C'], n)
        })

    # Verificação de colunas necessárias
    if 'Valor_R$' not in df.columns:
        st.error("O arquivo deve conter uma coluna chamada 'Valor_R$'")
        return

    # --- PROCESSAMENTO ESTATÍSTICO ---
    # Cálculo do Z-Score
    df['z_score'] = (df['Valor_R$'] - df['Valor_R$'].mean()) / df['Valor_R$'].std()
    df['Status'] = np.where(df['z_score'] > z_threshold, 'Inconsistente', 'Normal')
    
    anomalias = df[df['Status'] == 'Inconsistente'].copy()

    # --- MÉTRICAS ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Analisado", len(df))
    with m2:
        st.metric("Inconsistências", len(anomalias), delta=f"{len(anomalias)/len(df)*100:.1f}%", delta_color="inverse")
    with m3:
        st.metric("Valor sob Suspeita", f"R$ {anomalias['Valor_R$'].sum():,.2f}")

    st.divider()

    # --- GRÁFICOS ---
    col1, col2 = st.columns(2)

    with col1:
        # Histograma
        fig_hist = px.histogram(
            df, x="Valor_R$", 
            color="Status",
            color_discrete_map={"Normal": "#636EFA", "Inconsistente": "#EF553B"},
            title="Distribuição de Valores e Alvos da Auditoria",
            labels={'Valor_R$': 'Valor (R$)'},
            nbins=30
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        # Dispersão (Correção do erro de TYPEERROR aqui)
        fig_scatter = px.scatter(
            df, 
            x=df.index, 
            y="Valor_R$", 
            color="Status",
            color_discrete_map={"Normal": "#636EFA", "Inconsistente": "#EF553B"},
            title="Dispersão Geral de Guias",
            hover_data=['ID_Guia', 'Prestador', 'z_score'] if 'ID_Guia' in df.columns else ['Valor_R$']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- TABELA DETALHADA ---
    st.write("### 🔍 Detalhamento de Inconsistências")
    if not anomalias.empty:
        st.dataframe(
            anomalias.sort_values(by='z_score', ascending=False),
            use_container_width=True
        )
        
        # Botão para baixar resultados
        csv = anomalias.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Relatório de Inconsistências (CSV)",
            data=csv,
            file_name='relatorio_audit.csv',
            mime='text/csv',
        )
    else:
        st.success("Nenhuma guia ultrapassou o limite de segurança estabelecido.")

if __name__ == "__main__":
    main()
