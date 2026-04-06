import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="Portal Laboratório CDV", 
    layout="wide", 
    page_icon="🔬",
    initial_sidebar_state="collapsed"
)

# 2. Estilização CSS (Incluso comando para esconder o menu lateral)
st.markdown("""
    <style>
    [data-testid="stSidebar"], .st-emotion-cache-163ttbj, #MainMenu, footer, header {
        visibility: hidden;
        display: none;
    }
    
    .stApp { background-color: #f4f7f6; }
    .block-container { padding-top: 3rem; }

    .org-banner {
        background-color: #004d5a;
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
        text-transform: uppercase;
        font-weight: 800;
        color: white !important;
    }

    .app-card {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        border-top: 5px solid #006b80;
        text-align: center;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05);
    }

    .stButton button {
        background-color: #006b80 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 65px !important;
        width: 100% !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
    }
    .stButton button:hover {
        background-color: #004d5a !important;
        transform: translateY(-3px);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho
st.markdown("""
    <div class="org-banner">
        <p style="color: #00b4b4; font-weight: 500;">SISTEMA DE GESTÃO TÉCNICA</p>
        <h1>LABORATÓRIO CDV</h1>
        <div style="width: 60px; height: 3px; background-color: #00b4b4; margin: 15px auto;"></div>
    </div>
""", unsafe_allow_html=True)
# --- ADICIONE ESTE CSS EXTRA NO SEU BLOCO DE STYLE ---
# Este CSS faz com que o botão preencha o card e pareça parte dele
st.markdown("""
    <style>
    .card-container {
        position: relative;
        height: 250px; /* Altura fixa para alinhar os cards */
    }
    
    /* Esconde o design padrão do botão e o expande */
    .stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100% !important;
        height: 100% !important;
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
    }

    .stButton > button:hover {
        background-color: rgba(0, 107, 128, 0.05) !important; /* Leve destaque no hover */
        border: 2px solid #00b4b4 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Miolo Central
col_esq, col_central, col_dir = st.columns([0.5, 2, 0.5])

with col_central:
    c1, c2 = st.columns(2)

    # --- CARD DATALOGGER ---
    with c1:
        st.markdown("""
            <div class="card-container">
                <div class="app-card" style="height: 100%;">
                    <span style='font-size: 50px;'>📊</span>
                    <h2 style='color: #333; margin-top: 15px;'>Datalogger</h2>
                    <p style='color: #666;'>Inspeção de canais, sensores e telemetria.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # O botão fica invisível por cima de todo o HTML acima
        if st.button("Abrir Datalogger", key="btn_dl"):
            st.switch_page("pages/Datalogger.py")

    # --- CARD MODEM BGAN ---
    with c2:
        st.markdown("""
            <div class="card-container">
                <div class="app-card" style="height: 100%;">
                    <span style='font-size: 50px;'>📡</span>
                    <h2 style='color: #333; margin-top: 15px;'>Modem BGAN</h2>
                    <p style='color: #666;'>Teste de apontamento, sinal C/No e registro IP.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Abrir BGAN", key="btn_bgan"):
            st.switch_page("pages/BGAN.py")
# 5. Rodapé
st.markdown("<br><br><p style='text-align: center; color: #888;'>© 2026 Laboratório CDV</p>", unsafe_allow_html=True)
