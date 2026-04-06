import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from fpdf import FPDF
import os

# --- AJUSTE DE FUSO HORÁRIO ---
def get_br_now():
    tz_br = timezone(timedelta(hours=-3))
    return datetime.now(tz_br)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Laboratório CDV - Avaliação BGAN", page_icon="📡", layout="wide")

LOGO_PATH = os.path.join(os.getcwd(), "logo.png")

# --- CLASSE PDF REVISADA ---
class PDF_BGAN(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 107, 128) 
        self.cell(190, 10, 'RELATÓRIO DE AVALIAÇÃO TÉCNICA', 0, 1, 'R')
        self.set_draw_color(0, 180, 180)
        self.line(10, 25, 200, 25)
        self.ln(12)

    def secao_titulo(self, titulo):
        self.set_fill_color(0, 107, 128)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, f" {titulo}", 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def linha_teste(self, nome, status, largura=190):
        self.set_font('Arial', '', 8)
        self.set_text_color(60, 60, 60)
        self.cell(largura * 0.75, 5, f"  > {nome}", 0, 0, 'L')
        
        status_positivos = ["OK", "Registrado", "Ativo", "Aprovado", "Sim"]
        if any(pos in str(status) for pos in status_positivos):
            self.set_text_color(0, 120, 0)
        else:
            self.set_text_color(200, 0, 0)
            
        self.cell(largura * 0.25, 5, f"[ {status} ]", 0, 1, 'R')
        self.set_text_color(0, 0, 0)

# --- INTERFACE STREAMLIT ---
st.title("📡 Laboratório CDV - Avaliação Modem BGAN")

tab1, tab2 = st.tabs(["📝 Teste de Campo/Bancada", "📊 Histórico"])

with tab1:
    st.subheader("1. Identificação e Cronologia")
    c1, c2, c3 = st.columns(3)
    os_in = c1.text_input("OS*")
    serial_in = c1.text_input("Nº de Série (S/N)*")
    resp_in = c1.text_input("Operador*")
    
    fab_in = c2.selectbox("Fabricante*", ["-", "Hughes"])
    mod_in = c2.selectbox("Modelo*", ["-", "9502"])
    
    # Datas de uso
    data_primeiro_uso = c3.date_input("Data do Primeiro Uso", value=None)
    data_campo = c3.date_input("Data de Instalação em Campo", value=None)

    st.divider()
    st.subheader("🛠️ Checklist de Configuração Sequencial")
    
    # Fluxo simplificado para o exemplo
    p1 = st.checkbox("1. Protocolo TCP/IP em modo automático?")
    p_final = False
    if p1:
        if st.checkbox("2. Página WebUI (192.168.128.100) carregada?"):
            with st.expander("Configurações Internas", expanded=True):
                c_ok = st.checkbox("Confirmar: APN Stratos/Wiltd, Watchdog On, Remote SMS On")
                if c_ok: p_final = True

    if p_final:
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("2. Qualidade de Sinal")
            cno_nivel = st.number_input("Nível de Sinal (dBHz)", 0.0, 80.0, 0.0)
            eth_status = st.selectbox("Porta Ethernet*", ["-", "OK", "Danificada"])
            sim_status = st.selectbox("Slot SIM Card*", ["-", "OK", "Mau Contato"])

        with col_b:
            st.subheader("3. Parecer Técnico")
            real_time = st.selectbox("Real Time*", ["-", "OK", "FALHA"])
            parecer = st.selectbox("Resultado Final*", ["-", "Aprovado para Uso", "Aguardando Manutenção", "Reprovado"])
        
        ressalvas = st.text_area("Observações Técnicas")

        if st.button("🚀 GERAR RELATÓRIO PDF"):
            if "-" in [os_in, serial_in, eth_status, sim_status, real_time, parecer]:
                st.error("🚨 Preencha todos os campos obrigatórios (*)")
            else:
                pdf = PDF_BGAN()
                pdf.add_page()
                
                # --- SEÇÃO 1: IDENTIFICAÇÃO (SEM |) ---
                pdf.secao_titulo("1. IDENTIFICAÇÃO E HISTÓRICO")
                pdf.set_font('Arial', 'B', 9)
                
                # Linha 1
                pdf.cell(20, 6, "DATA TESTE:"); pdf.set_font('Arial', '', 9); pdf.cell(50, 6, get_br_now().strftime('%d/%m/%Y %H:%M'));
                pdf.set_font('Arial', 'B', 9); pdf.cell(15, 6, "OS:"); pdf.set_font('Arial', '', 9); pdf.cell(40, 6, os_in);
                pdf.set_font('Arial', 'B', 9); pdf.cell(20, 6, "SERIAL:"); pdf.set_font('Arial', '', 9); pdf.cell(45, 6, serial_in); pdf.ln()
                
                # Linha 2
                pdf.set_font('Arial', 'B', 9); pdf.cell(20, 6, "MODELO:"); pdf.set_font('Arial', '', 9); pdf.cell(50, 6, f"{fab_in} {mod_in}");
                pdf.set_font('Arial', 'B', 9); pdf.cell(20, 6, "RESP.:"); pdf.set_font('Arial', '', 9); pdf.cell(100, 6, resp_in); pdf.ln(8)

                # --- CÁLCULO DE TEMPO ---
                hoje = get_br_now().date()
                tempo_total = f"{(hoje - data_primeiro_uso).days} dias" if data_primeiro_uso else "Não informado"
                tempo_campo = f"{(hoje - data_campo).days} dias" if data_campo else "Não informado"

                pdf.set_font('Arial', 'B', 8); pdf.set_text_color(100, 100, 100)
                pdf.cell(95, 5, f"TEMPO DESDE PRIMEIRO USO: {tempo_total}", 0, 0)
                pdf.cell(95, 5, f"TEMPO EM CAMPO (ÚLT. INSTALAÇÃO): {tempo_campo}", 0, 1)
                pdf.ln(4)

                # --- SEÇÃO 2: RESULTADOS ---
                pdf.secao_titulo("2. CHECKLIST TÉCNICO")
                pdf.linha_teste("Nível de Sinal C/No", f"{cno_nivel} dBHz")
                pdf.linha_teste("Integridade da Porta Ethernet", eth_status)
                pdf.linha_teste("Integridade do Slot SIM Card", sim_status)
                pdf.linha_teste("Comunicação em Tempo Real", real_time)
                pdf.ln(6)

                # --- SEÇÃO 3: PARECER COM CORES DINÂMICAS ---
                pdf.secao_titulo("3. PARECER FINAL")
                
                if parecer == "Aprovado para Uso":
                    cor_status = (0, 107, 128) # Azul do seu tema
                elif parecer == "Aguardando Manutenção":
                    cor_status = (255, 140, 0) # Laranja
                else:
                    cor_status = (200, 0, 0)   # Vermelho
                
                pdf.set_text_color(*cor_status)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, f"RESULTADO: {parecer.upper()}", 0, 1, 'C')
                
                pdf.set_font('Arial', 'I', 9); pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 6, f"Observações: {ressalvas if ressalvas.strip() else 'Nenhuma.'}", border=1)

                # Gerar download
                pdf_output = pdf.output(dest='S')
                st.download_button(
                    "⬇️ Baixar Relatório PDF", 
                    data=pdf_output if isinstance(pdf_output, bytes) else pdf_output.encode('latin-1'), 
                    file_name=f"Relatorio_BGAN_{serial_in}.pdf"
                )
