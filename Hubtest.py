import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="Portal Laboratório CDV", 
    layout="wide", 
    page_icon="🔬",
    initial_sidebar_state="collapsed"
)

# 2. Estilização CSS Avançada
st.markdown("""
    <style>
    /* Esconder menus e elementos padrão do Streamlit */
    [data-testid="stSidebar"], .st-emotion-cache-163ttbj, #MainMenu, footer, header {
        visibility: hidden;
        display: none;
    }
    
    /* Fundo da página e container principal */
    .stApp {
        background-color: #f4f7f6;
    }
    
    .block-container {
        padding-top: 3rem;
    }

    /* Banner de Destaque da Organização */
    .org-banner {
        background-color: #004d5a; /* Tom mais escuro para seriedade */
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 40px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    
    .org-banner h1 {
        margin: 0;
        font-size: 2.8rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 800;
        color: #ffffff !important;
    }
    
    .org-banner p {
        margin-top: 5px;
        font-size: 1.1rem;
        color: #00b4b4;
        font-weight: 500;
    }

    /* Card de Aplicativo */
    .app-card {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        border-top: 5px solid #006b80;
        text-align: center;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05);
    }

    /* Botão de Ação */
    .stButton button {
        background-color: #006b80 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 65px !important;
        width: 100% !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        border: none !important;
        transition: 0.4s ease;
        text-transform: uppercase;
        margin-top: 10px;
    }
    .stButton button:hover {
        background-color: #004d5a !important;
        transform: translateY(-3px);
        box-shadow: 0px 5px 15px rgba(0,107,128,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho com Ênfase na Organização
st.markdown("""
    <div class="org-banner">
        <p>SISTEMA DE GESTÃO TÉCNICA</p>
        <h1>LABORATÓRIO CDV</h1>
        <div style="width: 60px; height: 3px; background-color: #00b4b4; margin: 15px auto;"></div>
    </div>
""", unsafe_allow_html=True)

# 4. Área de Seleção de Módulos (Centralizado)
col_esq, col_central, col_dir = st.columns([1, 1.3, 1])

with col_central:
    # Card do Aplicativo Datalogger
    st.markdown("""
        <div class="app-card">
            <span style='font-size: 50px;'>📡</span>
            <h2 style='color: #333; margin-top: 15px; margin-bottom: 5px;'>Módulo Datalogger</h2>
            <p style='color: #666; font-size: 1rem; line-height: 1.5;'>
                Ambiente restrito para inspeção de hardware, verificação de conectividade e emissão de pareceres técnicos.
            </p>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    # Botão de Acesso
    if st.button("🚀 INICIAR OPERAÇÃO"):
        try:
            st.switch_page("pages/Datalogger.py")
        except:
            st.error("ERRO: O módulo 'pages/Datalogger.py' não foi encontrado.")

# 5. Rodapé Institucional
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; border-top: 1px solid #ddd; padding-top: 20px;'>
        <p style='color: #888; font-size: 0.9rem; margin-bottom: 0;'>
            © 2024 Laboratório CDV | Departamento de Manutenção e Ativos
        </p>
        <p style='color: #bbb; font-size: 0.8rem;'>Uso restrito e autorizado.</p>
    </div>
""", unsafe_allow_html=True)
