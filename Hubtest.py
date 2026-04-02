import streamlit as st
import pandas as pd
import os

# 1. Configuração da Página
st.set_page_config(page_title="Hub Laboratório CDV", layout="wide", page_icon="🔬")

# 2. Estilização CSS
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 28px; color: #006b80; }
    div[data-testid="stMetricLabel"] { font-weight: bold; }
    
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

# 3. Lógica de Dados e Cálculos
VALOR_UNITARIO = 13720.96

def carregar_dados():
    db_file = "historico.csv"
    if os.path.exists(db_file):
        try:
            return pd.read_csv(db_file, encoding='utf-8-sig')
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_historico = carregar_dados()
total_dl = len(df_historico) if not df_historico.empty else 0
economia_total = total_dl * VALOR_UNITARIO

# 4. Interface Principal
header_left, header_right = st.columns([8, 2])
with header_left:
    st.title("🔬 Hub de Testes Laboratoriais - CDV")
    st.markdown("### Gestão de Ativos e Impacto Financeiro")
with header_right:
    if st.button("🔄 Atualizar Dados"):
        st.rerun()

# 5. Painel de Métricas (Economia e Volume)
st.markdown("---")
col_metrics_1, col_metrics_2 = st.columns(2)

with col_metrics_1:
    # Formatação brasileira de moeda (R$ 1.000,00)
    valor_formatado = f"R$ {economia_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    st.metric("Economia Total Gerada", valor_formatado, help="Soma do valor de mercado de todos os Dataloggers testados/recuperados.")

with col_metrics_2:
    st.metric("Dataloggers Avaliados", f"{total_dl} unidades")

st.info(f"💡 **Indicador de Valor:** Cada Datalogger evitado de nova compra representa uma economia de **R$ 13.720,96**.")

# 6. Acesso ao Aplicativo
st.divider()
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    with st.container(border=True):
        st.markdown("### 📊 Datalogger")
        st.write("Iniciar nova inspeção de hardware e sinais.")
        if st.button("Acessar Avaliação DL", key="btn_dl"):
            st.switch_page("pages/Datalogger.py")

# 7. Tabela de Resumo
st.divider()
if not df_historico.empty:
    with st.expander("📊 Histórico Recente de Dataloggers", expanded=True):
        colunas_exibir = ['Data do Teste', 'OS', 'Serial', 'Parecer']
        colunas_disponiveis = [c for c in colunas_exibir if c in df_historico.columns]
        # Mostra os 10 mais recentes (do fim para o começo)
        st.dataframe(df_historico[colunas_disponiveis].iloc[::-1].head(10), use_container_width=True)
else:
    st.info("Aguardando registros no arquivo 'historico.csv' para calcular impacto.")
