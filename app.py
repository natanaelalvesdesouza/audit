import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go

# Configuração estética da página
st.set_page_config(
    page_title="Lumina IA | Auditoria Avançada",
    page_icon="🛡️",
    layout="wide"
)

# Estilização customizada via CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🛡️ Lumina IA - Auditoria de Inconsistências")
    st.subheader("Análise Estatística de Guias Médicas")

    # --- SIDEBAR ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2761/2761131.png", width=100)
    st.sidebar.header("Configurações de Auditoria")
    
    z_threshold = st.sidebar.slider(
        "Rigor da Auditoria (Z-Score)",
        min_value=1.0,
        max_value=4.0,
        value=2.5,
        step=0.1,
        help="Quanto maior o Z-Score, mais 'estranha' a guia deve ser para ser marcada."
    )

    # Cálculo da porcentagem teórica (Distribuição Normal)
    prob_teorica = stats.norm.sf(z_threshold) * 100

    st.sidebar.info(f"""
    **Filtro Atual:**
    - Detectando o topo **{prob_teorica:.2f}%** das anomalias.
    - Guias acima de **{z_threshold} desvios padrões** da média.
    """)

    # --- GERAÇÃO DE DADOS (Simulação Pró) ---
    @st.cache_data
    def load_data():
        np.random.seed(42)
        n_guias = 1000
        # Simula custos médicos (distribuição log-normal é mais realista para custos)
        custos = np.random.lognormal(mean=6, sigma=0.8, size=n_guias)
        df = pd.DataFrame({
            'ID_Guia': [f"G-{i:05d}" for i in range(n_guias)],
            'Valor_R$': custos,
            'Prestador': np.random.choice(['Clínica A', 'Hospital B', 'Laboratório C', 'Clínica D'], n_guias)
        })
        return df

    df = load_data()

    # Cálculo do Z-Score Real
    df['z_score'] = (df['Valor_R$'] - df['Valor_R$'].mean()) / df['Valor_R$'].std()
    anomalias = df[df['z_score'] > z_threshold].copy()

    # --- DASHBOARD ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total de Guias", f"{len(df)}")
    with m2:
        st.metric("Inconsistências", f"{len(anomalias)}", delta=f"{len(anomalias)/len(df)*100:.1f}%", delta_color="inverse")
    with m3:
        st.metric("Volume em Risco", f"R$ {anomalias['Valor_R$'].sum():,.2f}")

    st.divider()

    col_graph1, col_graph2 = st.columns(2)

    with col_graph1:
        st.write("### Distribuição de Custos")
        # Gráfico de Histograma Elegante
        fig_hist = px.histogram(
            df, x="Valor_R$", 
            nbins=50, 
            color_discrete_sequence=['#636EFA'],
            title="Frequência de Valores de Guias",
            labels={'Valor_R$': 'Valor da Guia (R$)'}
        )
        # Linha indicando onde começa a anomalia
        threshold_value = (z_threshold * df['Valor_R$'].std()) + df['Valor_R$'].mean()
        fig_hist.add_vline(x=threshold_value, line_dash="dash", line_color="red", annotation_text="Limite IA")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_graph2:
        st.write("### Análise de Dispersão (Outliers)")
        # Gráfico de Dispersão
        df['Status'] = np.where(df['z_score'] > z_threshold, 'Inconsistente', 'Normal')
        fig_scatter = px.scatter(
            df, x="ID_Guia", y="Valor_R$", 
            color="Status",
            color_manual={"Normal": "#636EFA", "Inconsistente": "#EF553B"},
            title="Dispersão de Guias por Valor",
            hover_data=['Prestador', 'z_score']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.write("### 📋 Detalhamento das Guias Suspeitas")
    if not anomalias.empty:
        st.dataframe(
            anomalias.sort_values(by='Valor_R$', ascending=False).style.format({'Valor_R$': 'R$ {:.2f}', 'z_score': '{:.2f}'}),
            use_container_width=True
        )
    else:
        st.success("Nenhuma irregularidade detectada com o rigor atual.")

if __name__ == "__main__":
    main()
