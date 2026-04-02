import streamlit as st
import pandas as pd
import os

# Configurações de Design
st.set_page_config(page_title="Hub Laboratório CDV", layout="wide", page_icon="🔬")

# Estilização Profissional
st.markdown("""
    <style>
    /* Estilo dos Cards de Métricas */
    div[data-testid="stMetricValue"] { font-size: 28px; color: #006b80; }
    div[data-testid="stMetricLabel"] { font-weight: bold; }
    
    /* Botões de Acesso */
    .stLinkButton a {
        background-color: #006b80 !important;
        border-radius: 10px !important;
        transition: 0.3s;
    }
    .stLinkButton a:hover {
        background-color: #00b4b4 !important;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CONTABILIZAÇÃO ---
def buscar_metricas():
    # Caminho do arquivo que o seu app de DL gera
    # Se estiverem na mesma pasta, ele lê direto
    db_dl = "historico.csv" 
    
    total_dl = 0
    if os.path.exists(db_dl):
        df = pd.read_csv(db_dl)
        total_dl = len(df)
    
    # Aqui você repetiria para o Windvane e Termo
    return total_dl

total_dl = buscar_metricas()

# --- INTERFACE ---
st.title("🔬 Hub de Testes Laboratoriais - CDV")
st.markdown("### Monitoramento em Tempo Real")

# Linha de Métricas (Contadores)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total de Equipamentos", total_dl + 0 + 0) # Soma dos outros quando houver
m2.metric("Dataloggers Testados", f"{total_dl} un")
m3.metric("Windvanes", "0 un")
m4.metric("Termohigrômetros", "0 un")

st.divider()

# Grid de Aplicativos
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 📊 Datalogger")
        st.info("Inspeção de hardware, sinais GSM/GPS e mapeamento de canais.")
        st.link_button("Abrir Avaliação DL", "https://testedatalogger.streamlit.app/", use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown("### 🌬️ Windvane")
        st.info("Análise elétrica dinâmica/estática e integridade física.")
        st.link_button("Abrir Avaliação WV", "https://windvane-j4smexlhjh7ahgmmda5wiu.streamlit.app/", use_container_width=True)

with col3:
    with st.container(border=True):
        st.markdown("### 🌡️ Termohigrômetro")
        st.info("Monitoramento de calibração, temperatura e umidade.")
        st.link_button("Abrir Avaliação Termo", "URL_AQUI", use_container_width=True)

# Tabela de Resumo Rápido (Opcional)
if total_dl > 0:
    with st.expander("📄 Ver últimos registros do Datalogger"):
        df_dl = pd.read_csv("historico.csv")
        st.table(df_dl[['Data do Teste', 'OS', 'Serial', 'Parecer']].tail(5))