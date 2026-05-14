# --- ÁREA DE UPLOAD E INGESTÃO DE DADOS ---
st.sidebar.divider()
st.sidebar.subheader("Importar Dados")
uploaded_file = st.sidebar.file_opener = st.sidebar.file_uploader(
    "Anexe sua base (CSV ou Excel)", 
    type=["csv", "xlsx"]
)

@st.cache_data
def carregar_dados(file):
    if file is not None:
        try:
            if file.name.endswith('.csv'):
                return pd.read_csv(file)
            else:
                return pd.read_excel(file)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return None
    return gerar_dados_audit() # Mantém o simulador se estiver vazio

# Chamada da função
df = carregar_dados(uploaded_file)
