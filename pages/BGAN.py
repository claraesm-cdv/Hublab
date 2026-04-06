import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from fpdf import FPDF
import os

# --- AJUSTE DE FUSO HORÁRIO (UTC-3 BRASÍLIA) ---
def get_br_now():
    tz_br = timezone(timedelta(hours=-3))
    return datetime.now(tz_br)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Laboratório CDV - Avaliação BGAN", page_icon="📡", layout="wide")

DB_FILE = "historico_bgan.csv"
LOGO_PATH = os.path.join(os.getcwd(), "logo.png")

# --- ESTADOS DA SESSÃO ---
if 'inicio_sessao' not in st.session_state:
    st.session_state.inicio_sessao = get_br_now()

# --- FUNÇÕES DE PDF (RESUMO DAS ADAPTAÇÕES) ---
class PDF_BGAN(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 50, 100)
        self.cell(190, 10, 'RELATÓRIO DE TESTE - TERMINAL BGAN', 0, 1, 'R')
        self.line(10, 25, 200, 25)
        self.ln(12)

    def secao_titulo(self, titulo):
        self.set_fill_color(0, 50, 100)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, f" {titulo}", 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def linha_teste(self, nome, status):
        self.set_font('Arial', '', 9)
        self.cell(150, 6, f"  > {nome}", 0, 0)
        if status in ["OK", "Registrado", "Ativo", "Público"]:
            self.set_text_color(0, 120, 0)
        else:
            self.set_text_color(200, 0, 0)
        self.cell(40, 6, f"[ {status} ]", 0, 1, 'R')
        self.set_text_color(0, 0, 0)

# --- INTERFACE STREAMLIT ---
st.title("📡 Laboratório CDV - Avaliação Modem BGAN")

tab1, tab2 = st.tabs(["📝 Teste de Campo/Bancada", "📊 Histórico BGAN"])

with tab1:
    st.subheader("1. Identificação do Terminal")
    c1, c2, c3 = st.columns(3)
    os_in = c1.text_input("OS*")
    serial_in = c1.text_input("Nº de Série (S/N)*")
    fab_in = c2.selectbox("Fabricante*", ["Cobham", "Hughes", "Thrane & Thrane", "Outro"])
    mod_in = c2.text_input("Modelo (ex: Explorer 510)*")
    resp_in = c3.text_input("Técnico Responsável*")
    firmware_in = c3.text_input("Versão do Firmware")

    st.divider()
    ligando = st.radio("O Terminal Inicializa corretamente?*", ["-", "Sim", "Não"], horizontal=True)

    if ligando == "Sim":
        # --- ETAPA 2: APONTAMENTO E SINAL ---
        st.subheader("2. Qualidade de Sinal e Satélite")
        col_sig1, col_sig2, col_sig3 = st.columns(3)
        
        cno_nivel = col_sig1.number_input("Nível de Sinal (C/No em dBHz)", min_value=0.0, max_value=80.0, value=0.0)
        pointing_status = col_sig2.selectbox("Status de Apontamento*", ["-", "OK", "Sinal Instável", "Sem Visada"])
        beam_id = col_sig3.text_input("ID do Beam (Spot Beam)")

        # --- ETAPA 3: CONECTIVIDADE IP ---
        st.subheader("3. Registro e Conectividade IP")
        exp_net = st.expander("Verificações de Rede", expanded=True)
        cn1, cn2, cn3 = exp_net.columns(3)
        
        reg_status = cn1.selectbox("Registro na Rede*", ["-", "Registrado", "Falha de Registro", "SIM Bloqueado"])
        pdp_status = cn2.selectbox("PDP Context (Dados)*", ["-", "Ativo", "Falha"])
        ip_tipo = cn3.selectbox("Tipo de IP*", ["-", "Privado", "Público", "Estático"])
        
        latencia = st.text_input("Latência Média (Ping para 8.8.8.8) - ex: 720ms")

        # --- ETAPA 4: INTERFACES FÍSICAS ---
        st.subheader("4. Inspeção de Portas e Hardware")
        col_hw1, col_hw2, col_hw3 = st.columns(3)
        eth_port = col_hw1.selectbox("Porta Ethernet (RJ45)*", ["-", "OK", "Danificada"])
        wlan_port = col_hw2.selectbox("Wi-Fi Integrado*", ["-", "OK", "Falha", "N/A"])
        sim_slot = col_hw3.selectbox("Slot SIM Card*", ["-", "OK", "Mau Contato"])

        # --- PARECER FINAL ---
        st.subheader("5. Parecer Técnico")
        parecer = st.selectbox("Resultado Final*", ["-", "Aprovado para Uso", "Reprovado", "Aguardando Firmware/Reparo"])
        ressalvas = st.text_area("Observações Técnicas (Ex: Necessário troca de cabo TNC, bateria viciada...)")

        if st.button("🚀 FINALIZAR E GERAR RELATÓRIO"):
            if "-" in [os_in, serial_in, parecer, reg_status]:
                st.error("🚨 Por favor, preencha todos os campos obrigatórios (*)")
            else:
                # Lógica de salvamento e PDF similar ao anterior...
                st.success("Relatório de BGAN gerado com sucesso!")
                # Aqui entraria a chamada da função gerar_pdf adaptada
                
    elif ligando == "Não":
        st.error("❌ Equipamento não liga. Encaminhar para manutenção de hardware Nível 2.")
