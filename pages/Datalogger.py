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

# --- CLASSE PDF ESTILIZADA ---
class PDF_BGAN(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 107, 128) # Azul Petróleo
        self.cell(190, 10, 'RELATÓRIO DE AVALIAÇÃO TÉCNICA - BGAN', 0, 1, 'R')
        self.set_draw_color(0, 180, 180) # Linha Turquesa
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
        
        status_positivos = ["OK", "Registrado", "Ativo", "Aprovado para Uso", "Sim", "Aprovado"]
        
        if any(pos in status for pos in status_positivos):
            self.set_text_color(0, 120, 0)
            self.cell(largura * 0.25, 5, f"[ {status} ]", 0, 1, 'R')
        else:
            self.set_text_color(200, 0, 0)
            self.cell(largura * 0.25, 5, f"[ {status} ]", 0, 1, 'R')
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
    
    # Lógica simplificada de cascata para o Streamlit
    p_final = False
    if p1:
        st.info("🔗 Acesse o WebUI: http://192.168.128.100")
        if st.checkbox("2. Página inicial do equipamento carregada?"):
            with st.expander("Passos de Configuração Interna", expanded=True):
                c_a = st.checkbox("3. Connections > Manage Contexts (APN STRATOS/WILTD)")
                c_b = st.checkbox("4. Connections > Automatic Contexts (Static IP ACA: 1)")
                c_c = st.checkbox("5. Settings > Ethernet (Wake On LAN: Off)")
                c_d = st.checkbox("6. Settings > ATC Setup (Robustness: Off)")
                c_e = st.checkbox("7. M2M (Watchdog & Always On: Ativos)")
                c_f = st.checkbox("8. Security (Remote SMS Control: On)")
                
                if all([c_a, c_b, c_c, c_d, c_e, c_f]):
                    p_final = True

    # --- LIBERAÇÃO DO FORMULÁRIO FINAL ---
    if p_final:
        st.divider()
        st.success("✅ Configurações validadas. Prossiga para os testes finais.")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("2. Qualidade de Sinal")
            cno_nivel = st.number_input("Nível de Sinal (dBHz)", 0.0, 80.0, 0.0)
            
            st.subheader("3. Inspeção de Hardware")
            eth_status = st.selectbox("Porta Ethernet*", ["-", "OK", "Danificada"])
            sim_status = st.selectbox("Slot SIM Card*", ["-", "OK", "Mau Contato"])

        with col_b:
            st.subheader("4. Conexão com o Datalogger")
            real_time = st.selectbox("Real Time*", ["-", "OK", "FALHA"])
            
            st.subheader("5. Parecer Técnico")
            parecer = st.selectbox("Resultado Final*", ["-", "Aprovado para Uso", "Reprovado", "Aguardando Manutenção"])
        
        ressalvas = st.text_area("Observações Técnicas / Ressalvas")

        if st.button("🚀 FINALIZAR E GERAR RELATÓRIO"):
            if "-" in [os_in, serial_in, eth_status, sim_status, real_time, parecer]:
                st.error("🚨 Preencha todos os campos obrigatórios (*)")
            else:
                # --- GERAÇÃO DO PDF COM O NOVO ESTILO ---
                pdf = PDF_BGAN()
                pdf.set_auto_page_break(auto=True, margin=10)
                pdf.add_page()
                
                # Data no topo
                pdf.set_font('Arial', 'I', 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Data da Inspeção: {get_br_now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'R')
                pdf.ln(2)

                # Seção 1: Identificação
                pdf.secao_titulo("1. IDENTIFICAÇÃO DO EQUIPAMENTO")
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(25, 6, "OS:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, os_in, 0)
                pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Serial:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, serial_in, 0); pdf.ln()
                pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Fabricante:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, fab_in, 0)
                pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Modelo:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, mod_in, 0); pdf.ln()
                pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Operador:", 0); pdf.set_font('Arial', '', 9); pdf.cell(165, 6, resp_in, 0); pdf.ln(8)

                # Seção 2: Testes
                pdf.secao_titulo("2. CHECKLIST DE HARDWARE E SINAIS")
                
                # Subgrupo Sinal
                pdf.set_font('Arial', 'B', 8); pdf.set_text_color(0, 107, 128)
                pdf.cell(0, 6, "Qualidade de Link", 0, 1)
                pdf.linha_teste("Nível de Sinal C/No", f"{cno_nivel} dBHz")
                pdf.ln(2)

                # Subgrupo Hardware
                pdf.set_font('Arial', 'B', 8); pdf.set_text_color(0, 107, 128)
                pdf.cell(0, 6, "Interfaces Físicas", 0, 1)
                pdf.linha_teste("Porta Ethernet LAN", eth_status)
                pdf.linha_teste("Slot SIM Card", sim_status)
                pdf.ln(2)

                # Subgrupo Integração
                pdf.set_font('Arial', 'B', 8); pdf.set_text_color(0, 107, 128)
                pdf.cell(0, 6, "Comunicação", 0, 1)
                pdf.linha_teste("Integração Datalogger (Real Time)", real_time)
                pdf.ln(6)

                # Seção 3: Parecer
                pdf.secao_titulo("3. PARECER FINAL")
                cor_parecer = (0, 120, 0) if parecer == "Aprovado para Uso" else (200, 0, 0)
                pdf.set_text_color(*cor_parecer)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"STATUS FINAL: {parecer.upper()}", 0, 1, 'C')
                
                pdf.set_font('Arial', 'I', 9)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 6, f"Observações Técnicas: {ressalvas if ressalvas.strip() else 'Nenhuma observação adicional.'}", border=1)

                # Output
                pdf_filename = f"Relatorio_BGAN_{serial_in}.pdf"
                pdf_output = pdf.output(dest='S') # Retorna como string/bytes dependendo da versão do fpdf
                
                st.download_button(
                    label="⬇️ Baixar Relatório PDF",
                    data=pdf_output if isinstance(pdf_output, bytes) else pdf_output.encode('latin-1'),
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
                st.success("✅ Relatório gerado com sucesso!")

    elif p1:
        st.warning("⚠️ Complete todos os passos do checklist de configuração para liberar os testes de sinal e hardware.")

with tab2:
    st.info("O histórico será listado aqui após a implementação da persistência de dados (CSV/DB).")
