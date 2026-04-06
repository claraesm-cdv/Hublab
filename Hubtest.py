import streamlit as st

# 1. Configuração da Página
st.set_page_config(page_title="Portal Laboratório CDV", layout="wide", page_icon="🔬")

# 2. Estilização CSS para botões de acesso
st.markdown("""
    <style>
    .stButton button {
        background-color: #006b80 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 80px !important;
        width: 100% !important;
        font-weight: bold !important;
        font-size: 20px !important;
        border: none !important;
        transition: 0.3s;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stButton button:hover {
        background-color: #00b4b4 !important;
        transform: scale(1.02);
    }
    /* Estilo do Card */
    .card-acesso {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #eee;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho
st.title("🔬 Hub de Aplicativos - Laboratório CDV")
st.write("Selecione a ferramenta de teste para iniciar o procedimento.")

st.divider()

# 4. Grid de Aplicativos
# Criamos colunas para centralizar ou adicionar novos apps no futuro
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
        <div class="card-acesso">
            <h2 style='color: #006b80; margin-bottom: 0;'>Datalogger</h2>
            <p style='color: #666;'>Teste de Sinais, Hardware e Registro de OS</p>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    if st.button("ABRIR AVALIAÇÃO"):
        try:
            st.switch_page("pages/Datalogger.py")
        except:
            st.error("Erro: O arquivo 'pages/Datalogger.py' não foi localizado.")

# 5. Placeholder para Futuros Apps (Opcional - apenas visual)
st.divider()
cols_futuro = st.columns(3)
with cols_futuro[0]:
    st.info("💡 Novos módulos serão adicionados aqui conforme a demanda.")

# 6. Rodapé
st.caption("v1.0 | Laboratório de Testes CDV")
