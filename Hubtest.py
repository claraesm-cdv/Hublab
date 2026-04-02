import streamlit as st
import pandas as pd
import os

# Configurações de Design
st.set_page_config(page_title="Hub Laboratório CDV", layout="wide", page_icon="🔬")

# Estilização Profissional
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 28px; color: #006b80; }
    div[data-testid="stMetricLabel"] { font-weight: bold; }
    .stLinkButton a {
        background-color: #006b80 !important;
        border-radius: 10px !important;
        transition: 0.3s;
        text-align: center;
    }
    .stLinkButton a:hover {
        background-color: #00b4b4 !important;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CONTABILIZAÇÃO ---
# @st.cache_data(ttl=60) # Opcional: atualiza a cada 60 segundos automaticamente
def buscar_dados():
    db_dl = "historico.csv" 
    if os.path.exists(db_dl):
        try:
            # use_cols evita carregar o arquivo inteiro na memória se for muito grande
            df = pd.read_csv(db_dl, encoding='utf-8-sig')
            return df
        except Exception as e:
            st.error(f"Erro ao ler banco de dados: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Carregar dados
df_historico = buscar_dados()
total_dl = len(df_historico) if not df_historico.empty else 0

# --- INTERFACE ---
header_col, refresh_col = st.columns([9, 1])
with header_col:
    st.title("🔬 Hub de Testes Laboratoriais - CDV")
    st.markdown("### Monitoramento em Tempo Real")
with refresh_col:
    if st.button("🔄"): # Botão rápido para atualizar os números
        st.rerun()

# Linha de Métricas
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Geral", total_dl) 
m2.metric("Dataloggers", f"{total_dl} un")
m3.metric("Windvanes", "0 un")
m4.metric("Termohigrômetros", "0 un")

st.divider()

# Grid de Aplicativos (Cards)
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 📊 Datalogger")
        st.write("Inspeção de hardware e sinais.")
        st.link_button("Abrir Avaliação DL", "https://testedatalogger.streamlit.app/", use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown("### 🌬️ Windvane")
        st.write("Análise elétrica e física.")
        st.link_button("Abrir Avaliação WV", "https://windvane-j4smexlhjh7ahgmmda5wiu.streamlit.app/", use_container_width=True)

with col3:
    with st.container(border=True):
        st.markdown("### 🌡️ Termohigrômetro")
        st.write("Temperatura e umidade.")
        st.link_button("Abrir Avaliação Termo", "#", use_container_width=True)

st.divider()

# Tabela de Resumo Rápido
if not df_historico.empty:
    with st.expander("📄 Ver últimos registros do Datalogger", expanded=True):
        # Mostra apenas colunas essenciais e os últimos 5
        cols_viz = ['Data do Teste', 'OS', 'Serial', 'Parecer']
        # Filtra apenas se as colunas existirem no seu CSV
        cols_presentes = [c for c in cols_viz if c in df_historico.columns]
        st.table(df_historico[cols_presentes].tail(5))
else:
    st.info("Nenhum dado de Datalogger encontrado no arquivo 'historico.csv'.")
