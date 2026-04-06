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
st.set_page_config(page_title="Laboratório CDV - BGAN", page_icon="📡", layout="wide")

LOGO_PATH = os.path.join(os.getcwd(), "logo.png")

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'periodos' not in st.session_state:
    st.session_state.periodos = [{"entrada": get_br_now().date(), "saida": get_br_now().date()}]

# --- CLASSE PDF ESTILIZADA ---
class PDF_BGAN(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 107, 128) 
        self.cell(190, 10, 'RELATÓRIO DE AVALIAÇÃO TÉCNICA - BGAN', 0, 1, 'R')
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
        status_ok = ["OK", "Registrado", "Ativo", "Aprovado", "Sim"]
        color = (0, 120, 0) if any(x in str(status) for x in status_ok) else (200, 0, 0)
        self.set_text_color(*color)
        self.cell(largura * 0.25, 5, f"[ {status} ]", 0, 1, 'R')
        self.set_text_color(0, 0, 0)

# --- INTERFACE ---
st.title("📡 Laboratório CDV - Avaliação Modem BGAN")

tab1, tab2 = st.tabs(["📝 Teste de Campo/Bancada", "📊 Histórico"])

with tab1:
    st.subheader("1. Identificação do Terminal")
    c1, c2, c3 = st.columns(3)
    os_in = c1.text_input("OS*")
    serial_in = c2.text_input("Nº de Série (S/N)*")
    resp_in = c3.text_input("Operador*")
    
    fab_in = c1.selectbox("Fabricante*", ["-", "Hughes"])
    mod_in = c2.selectbox("Modelo*", ["-", "9502"])

    st.write("---")
    st.markdown("##### ⏳ Histórico de Passagens em Campo")
    
    for i, periodo in enumerate(st.session_state.periodos):
        col_p1, col_p2, col_p3 = st.columns([4, 4, 1])
        st.session_state.periodos[i]["entrada"] = col_p1.date_input(f"Entrada {i+1}", value=periodo["entrada"], key=f"ent_{i}")
        st.session_state.periodos[i]["saida"] = col_p2.date_input(f"Saída {i+1}", value=periodo["saida"], key=f"sai_{i}")
        
        if len(st.session_state.periodos) > 1:
            if col_p3.button("🗑️", key=f"del_{i}"):
                st.session_state.periodos.pop(i)
                st.rerun()

    if st.button("➕ Adicionar Passagem"):
        st.session_state.periodos.append({"entrada": get_br_now().date(), "saida": get_br_now().date()})
        st.rerun()

    # Cálculos de tempo
    dias_atividade = sum([(p["saida"] - p["entrada"]).days for p in st.session_state.periodos])
    primeira_entrada = min([p["entrada"] for p in st.session_state.periodos])
    dias_desde_primeiro = (get_br_now().date() - primeira_entrada).days

    c_res1, c_res2 = st.columns(2)
    c_res1.metric("Tempo desde 1º uso", f"{dias_desde_primeiro} dias")
    c_res2.metric("Tempo total em atividade", f"{dias_atividade} dias")

    st.divider()
    st.subheader("🛠️ Checklist de Configuração")
    p1 = st.checkbox("Configurações WebUI validadas (TCP/IP, APN, Watchdog)?")

    if p1:
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("2. Qualidade de Sinal")
            cno_nivel = st.number_input("Nível de Sinal (dBHz)", 0.0, 80.0, 0.0)
            eth_status = st.selectbox("Porta Ethernet*", ["-", "OK", "Danificada"])
            sim_status = st.selectbox("Slot SIM Card*", ["-", "OK", "Mau Contato"])
        with col_b:
            st.subheader("3. Parecer Técnico")
            real_time = st.selectbox("Real Time (Datalogger)*", ["-", "OK", "FALHA"])
            parecer = st.selectbox("Resultado Final*", ["-", "Aprovado para Uso", "Aguardando Manutenção", "Reprovado"])
        
        ressalvas = st.text_area("Observações Técnicas")

        if st.button("🚀 FINALIZAR E GERAR RELATÓRIO"):
            if "-" in [os_in, serial_in, eth_status, sim_status, real_time, parecer]:
                st.error("🚨 Preencha todos os campos obrigatórios (*)")
            else:
                pdf = PDF_BGAN()
                pdf.add_page()
                
                # 1. Identificação (Limpa, sem |)
                pdf.secao_titulo("1. IDENTIFICAÇÃO E CRONOLOGIA")
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(30, 6, "DATA TESTE:"); pdf.set_font('Arial', '', 9); pdf.cell(65, 6, get_br_now().strftime('%d/%m/%Y %H:%M'), 0)
                pdf.set_font('Arial', 'B', 9); pdf.cell(20, 6, "OS:"); pdf.set_font('Arial', '', 9); pdf.cell(75, 6, os_in, 0); pdf.ln()
                
                pdf.set_font('Arial', 'B', 9); pdf.cell(30, 6, "EQUIPAMENTO:"); pdf.set_font('Arial', '', 9); pdf.cell(65, 6, f"{fab_in} {mod_in}", 0)
                pdf.set_font('Arial', 'B', 9); pdf.cell(20, 6, "S/N:"); pdf.set_font('Arial', '', 9); pdf.cell(75, 6, serial_in, 0); pdf.ln()
                
                pdf.set_font('Arial', 'B', 9); pdf.cell(30, 6, "OPERADOR:"); pdf.set_font('Arial', '', 9); pdf.cell(160, 6, resp_in, 0); pdf.ln(8)

                # Tempos
                pdf.set_font('Arial', 'B', 8); pdf.set_text_color(100, 100, 100)
                pdf.cell(95, 5, f"TEMPO DESDE O PRIMEIRO USO: {dias_desde_primeiro} dias", 0, 0)
                pdf.cell(95, 5, f"TEMPO TOTAL EM ATIVIDADE EM CAMPO: {dias_atividade} dias", 0, 1)
                pdf.ln(4)

                # 2. Testes
                pdf.secao_titulo("2. RESULTADOS DOS TESTES")
                pdf.linha_teste("Nível de Sinal (C/No)", f"{cno_nivel} dBHz")
                pdf.linha_teste("Porta Ethernet Física", eth_status)
                pdf.linha_teste("Slot SIM Card", sim_status)
                pdf.linha_teste("Comunicação Real Time", real_time)
                pdf.ln(6)

                # 3. Parecer Final (Cores Dinâmicas)
                pdf.secao_titulo("3. PARECER FINAL")
                
                # Definição da cor do status final
                if parecer == "Aprovado para Uso":
                    cor_final = (0, 107, 128)   # Azul
                elif parecer == "Aguardando Manutenção":
                    cor_final = (255, 140, 0) # Laranja
                else:
                    cor_final = (200, 0, 0)   # Vermelho
                
                pdf.set_text_color(*cor_final)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, f"STATUS FINAL: {parecer.upper()}", 0, 1, 'C')
                
                pdf.set_font('Arial', 'I', 9); pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 6, f"Ressalvas: {ressalvas if ressalvas.strip() else 'Nenhuma.'}", border=1)

                # Download
                pdf_output = pdf.output(dest='S')
                st.download_button("⬇️ Baixar PDF", 
                                 data=pdf_output if isinstance(pdf_output, bytes) else pdf_output.encode('latin-1'), 
                                 file_name=f"Relatorio_BGAN_{serial_in}.pdf")
