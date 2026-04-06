import streamlit as st
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="Portal Laboratório CDV", 
    layout="wide", 
    page_icon="🔬"
)

# 2. Estilização CSS Personalizada
st.markdown("""
    <style>
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
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton button:hover {
        background-color: #00b4b4 !important;
        transform: scale(1.02);
        box-shadow: 4px 4px 10px rgba(0,0,0,0.15);
    }
    
    /* Estilo do Card de Acesso */
    .card-acesso {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #eaeaea;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        margin-bottom: -20px; /* Ajuste para aproximar do botão */
    }

    /* Centralizar o cabeçalho */
    .header-container {
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho com Logo e Título
st.markdown('<div class="header-container">', unsafe_allow_html=True)

# --- SEÇÃO DA LOGO ---
# MODO DE EXEMPLO (Imagem da Internet) - Remova esta linha quando tiver sua logo:
logo_url = "https://via.placeholder.com/150x80.png?text=LOGO+CDV" # Exemplo visual
st.image(logo_url, width=150)

# MODO RECOMENDADO (Sua Imagem Local):
# 1. Salve sua logo como 'logo.png' na mesma pasta deste script.
# 2. Descomente as 3 linhas abaixo e comente as 2 linhas do 'MODO DE EXEMPLO':
# image_path = os.path.join(os.path.dirname(__file__), 'logo.png')
# if os.path.exists(image_path):
#     st.image(image_path, width=180) # Ajuste a largura conforme necessário
# --------------------

st.title("Hub de Aplicativos")
st.markdown("<p style='font-size: 1.2rem; color: #666;'>Laboratório de Testes CDV</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 4. Grid de Aplicativos (Centralizado)
# Criamos colunas para centralizar o card no meio da tela
col_espaco_esq, col_central, col_espaco_dir = st.columns([1, 1.5, 1])

with col_central:
    # Card Visual
    st.markdown("""
        <div class="card-acesso">
            <h1 style='color: #006b80; font-size: 40px; margin-bottom: 10px;'>🔬</h1>
            <h2 style='color: #333; margin-bottom: 0;'>Datalogger</h2>
            <p style='color: #777; font-size: 1.1rem; margin-top: 10px;'>Teste de Sinais, Hardware e Registro de OS</p>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    # Botão de Ação (Abaixo do card para melhor UX no Streamlit)
    if st.button("Abrir Módulo de Avaliação"):
        try:
            # Certifique-se que o arquivo existe em: pages/Datalogger.py
            st.switch_page("pages/Datalogger.py")
        except:
            st.error("⚠️ Arquivo 'pages/Datalogger.py' não encontrado na estrutura do projeto.")

# 5. Rodapé
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #999; padding: 10px;'>"
    "v1.0 | Desenvolvimento Interno CDV"
    "</div>", 
    unsafe_allow_html=True
)
