import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

# Configuração da página
st.set_page_config(page_title="Lumina IA - Auditoria de Saúde", layout="wide")

def main():
    st.title("🛡️ Lumina IA - Monitoramento de Inconsistências")
    st.markdown("""
    Ajuste o rigor da análise. O Z-score identifica guias que fogem drasticamente do padrão 
    de custo ou frequência da cooperativa.
    """)

    # --- SIDEBAR DE CONFIGURAÇÕES ---
    st.sidebar.header("Parâmetros de Auditoria")
    
    # Slider para o Z-score
    z_threshold = st.sidebar.slider(
        "Defina o Limite de Z-score",
        min_value=1.0,
        max_value=4.0,
        value=2.5,
        step=0.1,
        help="Valores maiores tornam a auditoria mais rigorosa, focando apenas em anomalias extremas."
    )

    # Cálculo da porcentagem teórica baseada na distribuição normal (cauda superior)
    # stats.norm.sf é a Survival Function (1 - CDF), que dá a área à direita do Z
    porcentagem_identificada = stats.norm.sf(z_threshold) * 100

    # Mensagem dinâmica de impacto
    st.sidebar.info(
        f"**Impacto Estimado:**\n\n"
        f"Com Z > {z_threshold}, a IA identificará aproximadamente "
        f"**{porcentagem_identificada:.2f}%** das guias como as mais inconsistentes do sistema."
    )

    # --- SIMULAÇÃO DE DADOS (Substitua pela sua carga de dados real) ---
    st.subheader("Análise de Guias em Tempo Real")
    
    # Criando dados fictícios para demonstração
    data = pd.DataFrame({
        'ID_Guia': range(1001, 1101),
        'Valor_Procedimento': np.random.normal(500, 150, 100)
    })
    # Adicionando algumas anomalias manuais
    data.loc[0, 'Valor_Procedimento'] = 1500
    data.loc[1, 'Valor_Procedimento'] = 1200

    # Cálculo do Z-score real nos dados
    mean_val = data['Valor_Procedimento'].mean()
    std_val = data['Valor_Procedimento'].std()
    data['z_score'] = (data['Valor_Procedimento'] - mean_val) / std_val

    # Filtragem baseada no slider
    anomalias = data[data['z_score'] > z_threshold]

    # --- EXIBIÇÃO DOS RESULTADOS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total de Guias Analisadas", len(data))
        st.metric("Guias Inconsistentes Detectadas", len(anomalias), delta_color="inverse")

    with col2:
        st.write(f"**Distribuição de Probabilidade (Z-score > {z_threshold})**")
        # Exibição simples das anomalias
        if not anomalias.empty:
            st.dataframe(anomalias.sort_values(by='z_score', ascending=False))
        else:
            st.success("Nenhuma inconsistência extrema detectada com este nível de rigor.")

if __name__ == "__main__":
    main()
