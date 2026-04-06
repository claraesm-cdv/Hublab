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

# --- CLASSE PDF (LAYOUT IDENTICO AO DATALOGGER) ---
class PDF_BGAN_ESTILO_DL(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 107, 128) # Azul Datalogger
        self.cell(190, 10, 'RELATÓRIO DE INSPEÇÃO TÉCNICA - BGAN', 0, 1, 'R')
        self.set_draw_color(0, 180, 180) # Linha Turquesa
        self.line(10, 25, 200, 25)
        self.ln(12)

    def secao_titulo(self, titulo):
        self.set_fill_color(0, 107, 128) # Fundo Azul Datalogger
        self.set_font('Arial', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, f" {titulo}", 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def linha_teste(self, nome, status, largura=190):
        self.set_font('Arial', '', 8)
        self.set_text_color(60, 60, 60)
        self.cell(largura * 0.8, 5, f"  > {nome}", 0, 0, 'L')
        status_positivos = ["OK", "Aprovado", "Registrado", "Ativo", "Público", "Sim", "Aprovado para Uso"]
        if status in status_positivos:
            self.set_text_color(0, 120, 0)
            self.cell(largura * 0.2, 5, f"[ {status} ]", 0, 1, 'R')
        else:
            self.set_text_color(200, 0, 0)
            self.cell(largura * 0.2, 5, f"[ {status if status != '-' else 'FALHA'} ]", 0, 1, 'R')
        self.set_text_color(0, 0, 0)

def gerar_pdf_bgan(dados_id, parecer, ressalvas, checklist_detalhado):
    pdf = PDF_BGAN_ESTILO_DL()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    data_hoje = get_br_now().strftime("%d/%m/%Y %H:%M:%S")
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Data da Inspeção: {data_hoje}", 0, 1, 'R')
    pdf.ln(2)
    
    # 1. IDENTIFICAÇÃO
    pdf.secao_titulo("1. IDENTIFICAÇÃO DO TERMINAL BGAN")
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(25, 6, "OS:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["OS"]), 0)
    pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Serial:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["Serial"]), 0); pdf.ln()
    pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Fabricante:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["Fabricante"]), 0)
    pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Modelo:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["Modelo"]), 0); pdf.ln()
    pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Operador:", 0); pdf.set_font('Arial', '', 9); pdf.cell(165, 6, str(dados_id["Operador"]), 0); pdf.ln()
    pdf.ln(4)
    
    # 2. CHECKLIST DE CONFIGURAÇÃO (RESUMO)
    pdf.secao_titulo("2. VALIDAÇÃO DE CONFIGURAÇÃO (CHECKLIST)")
    for nome, status in checklist_detalhado.get("Configuração", {}).items():
        pdf.linha_teste(nome, status)
    pdf.ln(2)

    # 3. TESTES DE SINAL E HARDWARE
    pdf.secao_titulo("3. QUALIDADE DE SINAL E HARDWARE")
    for nome, status in checklist_detalhado.get("Testes", {}).items():
        pdf.linha_teste(nome, status)
    pdf.ln(4)

    # 4. PARECER FINAL
    pdf.secao_titulo("4. PARECER TÉCNICO")
    cor = (0, 120, 0) if "Aprovado" in parecer else (200, 0, 0)
    pdf.set_text_color(*cor); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"STATUS FINAL: {parecer.upper()}", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 9); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, f"Observações: {ressalvas if ressalvas.strip() else 'Nenhuma.'}", border=1)
    
    return pdf.output(dest='S').encode('latin1')

# --- INTERFACE ---
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
    
    # Dicionário para capturar o checklist no PDF
    st_cfg = {}
    
    p1 = st.checkbox("1. Protocolo TCP/IP: IP e DNS em modo automático?")
    st_cfg["Configuração TCP/IP"] = "OK" if p1 else "PENDENTE"

    p2 = False
    if p1:
        st.info("🔗 Acesse o WebUI: http://192.168.128.100")
        p2 = st.checkbox("2. Página inicial do equipamento carregada?")
        st_cfg["Acesso WebUI"] = "OK" if p2 else "PENDENTE"

    p3 = False
    if p2:
        with st.expander("3. Connections > Manage Contexts", expanded=True):
            st.markdown("- **APN:** STRATOS ou WILTD")
            p3 = st.checkbox("Configurações do Passo 3 conferem?")
            st_cfg["Manage Contexts"] = "OK" if p3 else "PENDENTE"

    # ... (Omitindo passos 4 a 7 para brevidade, mas seguem a mesma lógica)
    # Simulando a conclusão para o exemplo
    p8 = False
    if p3:
         p8 = st.checkbox("Passo 8: Configuração Finalizada?")
         st_cfg["Checklist Completo"] = "OK" if p8 else "PENDENTE"

    if p8:
        st.divider()
        st.success("✅ Configurações validadas. Prossiga para os testes finais.")
        
        st.subheader("2. Testes de Campo")
        cno_nivel = st.number_input("Nível de Sinal (dBHz)", 0.0, 80.0, 0.0)
        
        ch_hw1, ch_hw2 = st.columns(2)
        eth_status = ch_hw1.selectbox("Porta Ethernet*", ["-", "OK", "Danificada"])
        sim_status = ch_hw2.selectbox("Slot SIM Card*", ["-", "OK", "Mau Contato"])
        real_time = st.selectbox("Real Time*", ["-", "OK", "FALHA"])
        
        parecer = st.selectbox("Resultado Final*", ["-", "Aprovado para Uso", "Reprovado", "Aguardando Manutenção"])
        ressalvas = st.text_area("Observações Técnicas")

        if st.button("🚀 FINALIZAR E GERAR RELATÓRIO"):
            if "-" in [os_in, serial_in, eth_status, sim_status, real_time, parecer]:
                st.error("🚨 Preencha todos os campos obrigatórios!")
            else:
                dados_pdf = {
                    "OS": os_in, "Serial": serial_in, "Fabricante": fab_in, 
                    "Modelo": mod_in, "Operador": resp_in
                }
                
                checklist_final = {
                    "Configuração": st_cfg,
                    "Testes": {
                        "Nível de Sinal": f"{cno_nivel} dBHz",
                        "Porta Ethernet": eth_status,
                        "Slot SIM": sim_status,
                        "Real Time": real_time
                    }
                }
                
                pdf_bytes = gerar_pdf_bgan(dados_pdf, parecer, ressalvas, checklist_final)
                st.download_button("📥 Baixar PDF BGAN", data=pdf_bytes, 
                                 file_name=f"BGAN_{serial_in}.pdf", mime="application/pdf")
