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

# --- FUNÇÕES DE PDF ---
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
        if status in ["OK", "Registrado", "Ativo", "Público", "Aprovado", "Sim"]:
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
    fab_in = c2.selectbox("Fabricante*", ["-", "Hughes"])
    mod_in = c2.selectbox("Modelo*", ["-", "9502"])
    resp_in = c3.text_input("Operador*")

    st.divider()
    st.subheader("🛠️ Checklist de Configuração Sequencial")
    st.caption("Marque cada passo concluído para liberar o próximo.")

    # --- FLUXO DE CHECKBOXES SEQUENCIAIS ---
    
    # Passo 1
    p1 = st.checkbox("1. Protocolo TCP/IP: IP e DNS em modo automático?")

    # Passo 2
    p2 = False
    if p1:
        st.info("🔗 Acesse o WebUI: http://192.168.128.100")
        p2 = st.checkbox("2. Página inicial do equipamento carregada?")

    # Passo 3
    p3 = False
    if p2:
        with st.expander("3. Connections > Manage Contexts", expanded=True):
            st.markdown("""
            - **Owner:** 192.168.128.101
            - **Service:** Standard
            - **APN 1:** STRATOS.BGAN.INMARSAT.COM (Onixtec)
            - **APN 2:** WILTD.BGAN.INMARSAT.COM (Kintech)
            """)
            p3 = st.checkbox("Configurações do Passo 3 conferem?")

    # Passo 4
    p4 = False
    if p3:
        with st.expander("4. Connections > Automatic Contexts", expanded=True):
            st.markdown("""
            **Static IP ACA:** 1 | **Enable:** Off | **Service:** Standard  
            **DHCP Automatic Contexts:** Off
            """)
            p4 = st.checkbox("Configurações do Passo 4 conferem?")

    # Passo 5
    p5 = False
    if p4:
        with st.expander("5. Settings > Ethernet", expanded=True):
            st.markdown("""
            **Wake On LAN:** Off | **Idle Timeout:** 0 | **UTC Time:** 0000  
            **Ethernet Operation:** Default
            """)
            p5 = st.checkbox("Configurações do Passo 5 conferem?")

    # Passo 6
    p6 = False
    if p5:
        with st.expander("6. Settings > ATC Setup", expanded=True):
            st.write("**ATC Robustness:** Off")
            p6 = st.checkbox("Configurações do Passo 6 conferem?")

    # Passo 7
    p7 = False
    if p6:
        with st.expander("7. M2M (Watchdog & Always On)", expanded=True):
            st.markdown("""
            - **Context Watchdog:** On | **Ping IPs:** 8.8.8.8 / 8.8.4.4
            - **Time between Pings:** 240
            - **Always On Context:** On | **IP:** 192.168.128.101
            """)
            p7 = st.checkbox("Configurações do Passo 7 conferem?")

    # Passo 8
    p8 = False
    if p7:
        with st.expander("8. Security", expanded=True):
            st.write("**Remote SMS Control:** On | **Password:** remote")
            p8 = st.checkbox("Passo 8: Configuração Finalizada?")

    # --- LIBERAÇÃO DO FORMULÁRIO FINAL ---
    if p8:
        st.divider()
        st.success("✅ Configurações validadas. Prossiga para os testes de sinal.")
        
        st.subheader("2. Qualidade de Sinal e Satélite")
        col_sig1 = st.columns(1)
        cno_nivel = col_sig1.number_input("Nível de Sinal (dBHz)", 0.0, 80.0, 0.0)
    

        st.subheader("3. Inspeção de Hardware")
        ch1, ch2 = st.columns(2)
        eth_port = ch1.selectbox("Porta Ethernet*", ["-", "OK", "Danificada"])
        sim_slot = ch2.selectbox("Slot SIM Card*", ["-", "OK", "Mau Contato"])


        st.subheader("3. Conexão com o Datalogger")
        ch1= st.columns(1)
        eth_port = ch1.selectbox("Real Time*", ["-", "OK", "FALHA"])
        
        st.subheader("5. Parecer Técnico")
        parecer = st.selectbox("Resultado Final*", ["-", "Aprovado para Uso", "Reprovado", "Aguardando Manutenção"])
        ressalvas = st.text_area("Observações Técnicas")

        if st.button("🚀 FINALIZAR E GERAR RELATÓRIO"):
            if "-" in [os_in, serial_in, parecer, reg_status, pointing_status]:
                st.error("🚨 Preencha todos os campos obrigatórios (*)")
            else:
                # Geração de PDF simplificada para exemplo
                pdf = PDF_BGAN()
                pdf.add_page()
                pdf.secao_titulo("DADOS DO EQUIPAMENTO")
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, f"OS: {os_in} | S/N: {serial_in} | Operador: {resp_in}", 0, 1)
                
                pdf.ln(5)
                pdf.secao_titulo("RESULTADOS DOS TESTES")
                pdf.linha_teste("Sinal C/No", str(cno_nivel))
                pdf.linha_teste("Registro na Rede", reg_status)
                pdf.linha_teste("Conectividade de Dados", pdp_status)
                pdf.linha_teste("Porta Ethernet", eth_port)
                
                pdf.ln(5)
                pdf.secao_titulo("PARECER FINAL")
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 10, f"RESULTADO: {parecer}", 0, 1)
                pdf.set_font('Arial', 'I', 9)
                pdf.multi_cell(0, 5, f"Obs: {ressalvas}")

                pdf_output = f"Relatorio_{serial_in}.pdf"
                pdf.output(pdf_output)
                
                with open(pdf_output, "rb") as f:
                    st.download_button("⬇️ Baixar Relatório PDF", f, file_name=pdf_output)
                st.success("Relatório gerado!")

    elif p1:
        st.warning("⚠️ Você precisa completar o Checklist de Configuração (Passos 1 a 8) para liberar o formulário de aprovação.")

with tab2:
    st.info("O histórico de testes será exibido aqui após a integração com o banco de dados/CSV.")
