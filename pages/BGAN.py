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
        # Lógica de cores para o status
        if status in ["OK", "Registrado", "Ativo", "Público", "Aprovado para Uso", "Sim"]:
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
    p1 = st.checkbox("1. Protocolo TCP/IP: IP e DNS em modo automático?")

    p2 = False
    if p1:
        st.info("🔗 Acesse o WebUI: http://192.168.128.100")
        p2 = st.checkbox("2. Página inicial do equipamento carregada?")

    p3 = False
    if p2:
        with st.expander("3. Connections > Manage Contexts", expanded=True):
            st.markdown("- **Owner:** 192.168.128.101\n- **Service:** Standard\n- **APN:** STRATOS ou WILTD")
            p3 = st.checkbox("Configurações do Passo 3 conferem?")

    p4 = False
    if p3:
        with st.expander("4. Connections > Automatic Contexts", expanded=True):
            st.markdown("**Static IP ACA:** 1 | **Enable:** Off | **Service:** Standard")
            p4 = st.checkbox("Configurações do Passo 4 conferem?")

    p5 = False
    if p4:
        with st.expander("5. Settings > Ethernet", expanded=True):
            st.markdown("**Wake On LAN:** Off | **Idle Timeout:** 0 | **Ethernet:** Default")
            p5 = st.checkbox("Configurações do Passo 5 conferem?")

    p6 = False
    if p5:
        with st.expander("6. Settings > ATC Setup", expanded=True):
            st.write("**ATC Robustness:** Off")
            p6 = st.checkbox("Configurações do Passo 6 conferem?")

    p7 = False
    if p6:
        with st.expander("7. M2M (Watchdog & Always On)", expanded=True):
            st.markdown("- **Watchdog:** On (8.8.8.8) | **Always On:** On (192.168.128.101)")
            p7 = st.checkbox("Configurações do Passo 7 conferem?")

    p8 = False
    if p7:
        with st.expander("8. Security", expanded=True):
            st.write("**Remote SMS Control:** On | **Password:** remote")
            p8 = st.checkbox("Passo 8: Configuração Finalizada?")

    # --- LIBERAÇÃO DO FORMULÁRIO FINAL ---
    if p8:
        st.divider()
        st.success("✅ Configurações validadas. Prossiga para os testes finais.")
        
        st.subheader("2. Qualidade de Sinal")
        cno_nivel = st.number_input("Nível de Sinal (dBHz)", 0.0, 80.0, 0.0)
        
        st.subheader("3. Inspeção de Hardware")
        ch_hw1, ch_hw2 = st.columns(2)
        eth_status = ch_hw1.selectbox("Porta Ethernet*", ["-", "OK", "Danificada"])
        sim_status = ch_hw2.selectbox("Slot SIM Card*", ["-", "OK", "Mau Contato"])

        st.subheader("4. Conexão com o Datalogger")
        real_time = st.selectbox("Real Time*", ["-", "OK", "FALHA"])
        
        st.subheader("5. Parecer Técnico")
        parecer = st.selectbox("Resultado Final*", ["-", "Aprovado para Uso", "Reprovado", "Aguardando Manutenção"])
        ressalvas = st.text_area("Observações Técnicas")

        if st.button("🚀 FINALIZAR E GERAR RELATÓRIO"):
            if "-" in [os_in, serial_in, eth_status, sim_status, real_time, parecer]:
                st.error("🚨 Preencha todos os campos obrigatórios (*)")
            else:
                # Geração do PDF
                pdf = PDF_BGAN()
                pdf.add_page()
                
                pdf.secao_titulo("DADOS DO EQUIPAMENTO")
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, f"OS: {os_in} | S/N: {serial_in} | Fabricante: {fab_in} | Modelo: {mod_in}", 0, 1)
                pdf.cell(0, 6, f"Operador: {resp_in} | Data: {get_br_now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
                
                pdf.ln(5)
                pdf.secao_titulo("RESULTADOS DOS TESTES")
                pdf.linha_teste("Nível de Sinal (C/No)", f"{cno_nivel} dBHz")
                pdf.linha_teste("Porta Ethernet Física", eth_status)
                pdf.linha_teste("Slot SIM Card", sim_status)
                pdf.linha_teste("Comunicação Real Time (Datalogger)", real_time)
                
                pdf.ln(5)
                pdf.secao_titulo("PARECER FINAL")
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 10, f"RESULTADO: {parecer}", 0, 1)
                pdf.set_font('Arial', 'I', 9)
                pdf.multi_cell(0, 5, f"Observações: {ressalvas}")

                pdf_filename = f"Relatorio_BGAN_{serial_in}.pdf"
                pdf.output(pdf_filename)
                
                with open(pdf_filename, "rb") as f:
                    st.download_button("⬇️ Baixar Relatório PDF", f, file_name=pdf_filename)
                st.success("✅ Relatório gerado com sucesso!")

    elif p1:
        st.warning("⚠️ Complete o checklist de configuração para liberar os testes de sinal e hardware.")

with tab2:
    st.info("O histórico será listado aqui após a implementação da persistência de dados.")
