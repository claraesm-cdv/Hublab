import streamlit as st
import pandas as pd
import os

# 1. Configuração da Página
st.set_page_config(page_title="Hub Laboratório CDV", layout="wide", page_icon="🔬")

# 2. Estilização CSS (Melhoria visual dos botões e métricas)
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 28px; color: #006b80; }
    div[data-testid="stMetricLabel"] { font-weight: bold; }
    
    /* Estilizando os botões para parecerem Cards */
    .stButton button {
        background-color: #006b80 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 60px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #00b4b4 !important;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Lógica de Leitura de Dados (Sincronizada)
def carregar_dados():
    # Como agora estão na mesma máquina, o Hub lê o arquivo que o DL cria
    db_file = "historico.csv"
    if os.path.exists(db_file):
        try:
            return pd.read_csv(db_file, encoding='utf-8-sig')
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_historico = carregar_dados()

# Contabilização por equipamento (Baseado na coluna 'Equipamento' ou 'Modelo')
total_dl = len(df_historico) if not df_historico.empty else 0
# Você pode filtrar se tiver uma coluna identificando o tipo:
# total_dl = len(df_historico[df_historico['Equipamento'] == 'Datalogger'])

# 4. Interface Principal
header_left, header_right = st.columns([8, 2])
with header_left:
    st.title("🔬 Hub de Testes Laboratoriais - CDV")
    st.markdown("### Painel de Controle e Gestão de Equipamentos")
with header_right:
    if st.button("🔄 Atualizar Dados"):
        st.rerun()

# Linha de Métricas
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Geral", total_dl)
m2.metric("Dataloggers", f"{total_dl} un")
m3.metric("Windvanes", "0 un")
m4.metric("Termohigrômetros", "0 un")

st.divider()

# 5. Grid de Acesso aos Aplicativos
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 📊 Datalogger")
        st.info("Inspeção de hardware, sinais GSM/GPS e mapeamento de canais.")
        # IMPORTANTE: O nome dentro do switch_page deve ser o caminho do arquivo no GitHub
        if st.button("Acessar Avaliação DL", key="btn_dl"):
            st.switch_page("pages/Datalogger.py")

with col2:
    with st.container(border=True):
        st.markdown("### 🌬️ Windvane")
        st.info("Análise elétrica dinâmica/estática e integridade física.")
        if st.button("Acessar Avaliação WV", key="btn_wv"):
            st.switch_page("pages/Windvane.py")

with col3:
    with st.container(border=True):
        st.markdown("### 🌡️ Termohigrômetro")
        st.info("Monitoramento de calibração, temperatura e umidade.")
        if st.button("Acessar Avaliação Termo", key="btn_th"):
            # Substitua pelo nome do arquivo quando criar
            st.warning("Página em desenvolvimento")

st.divider()

# 6. Tabela de Resumo (Últimos Testes)
if not df_historico.empty:
    with st.expander("📊 Visualizar Últimos testes de Datalogger", expanded=True):
        # Seleciona apenas as colunas principais para não poluir o visual
        colunas_exibir = ['Data do Teste', 'OS', 'Serial', 'Parecer']
        # Filtra apenas colunas que realmente existem no seu CSV
        colunas_disponiveis = [c for c in colunas_exibir if c in df_historico.columns]
        st.dataframe(df_historico[colunas_disponiveis].tail(10), use_container_width=True)
else:
    st.info("Nenhum registro encontrado no arquivo 'historico.csv'.")
