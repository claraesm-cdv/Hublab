import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="Portal Laboratório CDV", 
    layout="wide", 
    page_icon="🔬",
    initial_sidebar_state="collapsed" # Tenta iniciar com o menu recolhido
)

# 2. Estilização CSS (Esconder menu lateral e personalizar botões)
st.markdown("""
    <style>
    /* Esconde o menu lateral (sidebar), o botão de menu e o footer do Streamlit */
    [data-testid="stSidebar"], .st-emotion-cache-163ttbj, #MainMenu, footer, header {
        visibility: hidden;
        display: none;
    }
    
    /* Remove o preenchimento do topo para centralizar mais o conteúdo */
    .block-container {
        padding-top: 5rem;
    }

    /* Estilo do Botão Principal */
    .stButton button {
        background-color: #006b80 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 70px !important;
        width: 100% !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border: none !important;
        transition: 0.3s;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        text-transform: uppercase;
    }
    .stButton button:hover {
        background-color: #00b4b4 !important;
        transform: scale(1.02);
    }
    
    /* Estilo do Card de Acesso */
    .card-acesso {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 20px;
        border: 1px solid #eee;
        text-align: center;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.05);
    }

    .header-text {
        text-align: center;
        margin-bottom: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho Minimalista
st.markdown("""
    <div class="header-text">
        <h1 style='color: #006b80; font-size: 2.5rem;'>Hub de Aplicativos</h1>
        <p style='color: #666; font-size: 1.2rem;'>Laboratório de Testes CDV</p>
    </div>
""", unsafe_allow_html=True)

# 4. Centralização do App Único
col_esq, col_central, col_dir = st.columns([1, 1.2, 1])

with col_central:
    # Card Visual
    st.markdown("""
        <div class="card-acesso">
            <h1 style='font-size: 50px; margin-bottom: 10px;'>📊</h1>
            <h2 style='color: #333; margin-top: 0;'>Datalogger</h2>
            <p style='color: #777; margin-bottom: 25px;'>Clique no botão abaixo para iniciar a avaliação técnica do equipamento.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Botão posicionado logo abaixo do card
    if st.button("ACESSAR MÓDULO"):
        try:
            st.switch_page("pages/Datalogger.py")
        except:
            st.error("Erro: 'pages/Datalogger.py' não encontrado.")

# 5. Rodapé discreto
st.markdown("<br><br><p style='text-align: center; color: #bbb; font-size: 0.8rem;'>v1.0 | Interno</p>", unsafe_allow_html=True)
