import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from fpdf import FPDF
import os

# --- AJUSTE DE FUSO HORÁRIO (Brasília) ---
def get_br_now():
    tz_br = timezone(timedelta(hours=-3))
    return datetime.now(tz_br)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Laboratório CDV - BGAN", page_icon="📡", layout="wide")

LOGO_PATH = os.path.join(os.getcwd(), "logo1.png")

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

    def linha_teste(self, nome, status, cor_custom=None):
        self.set_font('Arial', '', 8)
        self.set_text_color(60, 60, 60)
        self.cell(142.5, 5, f"  > {nome}", 0, 0, 'L')
        
        # Lógica de cores automática se não houver cor customizada
        if cor_custom:
            color = cor_custom
        else:
            status_ok = ["OK", "Registrado", "Ativo", "Aprovado", "Sim", "Configurado"]
            color = (0, 120, 0) if any(x in str(status) for x in status_ok) else (200, 0, 0)
        
        self.set_text_color(*color)
        self.cell(47.5, 5, f"[ {status} ]", 0, 1, 'R')
        self.set_text_color(0, 0, 0)

# --- INTERFACE ---
st.title("📡 Laboratório CDV - Avaliação Modem BGAN")

tab1, tab2 = st.tabs(["📝 Verificação do equipamento", "📊 Histórico"])

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

    dias_atividade = sum([(p["saida"] - p["entrada"]).days for p in st.session_state.periodos])
    primeira_entrada = min([p["entrada"] for p in st.session_state.periodos])
    dias_desde_primeiro = (get_br_now().date() - primeira_entrada).days

    c_res1, c_res2 = st.columns(2)
    c_res1.metric("Tempo desde 1º uso", f"{dias_desde_primeiro} dias")
    c_res2.metric("Tempo total em atividade", f"{dias_atividade} dias")

    st.divider()
    st.subheader("🛠️ Checklist de Configuração Sequencial (WebUI)")

    # --- FLUXO SEQUENCIAL ---
    step1 = st.checkbox("1. Protocolo TCP/IP: IP e DNS em modo automático?")
    step_final_valid = False
    
    if step1:
        st.info("🔗 Acesse o WebUI: http://192.168.128.100")
        if st.checkbox("2. Página inicial do equipamento carregada?"):
            st.markdown("---")
            if st.checkbox("3. Connections > Manage Contexts (APN STRATOS/WILTD)"):
                if st.checkbox("4. Connections > Automatic Contexts (Static ACA: 1)"):
                    if st.checkbox("5. Settings > Ethernet (WoL: Off / Idle: 0)"):
                        if st.checkbox("6. Settings > ATC Setup (Robustness: Off)"):
                            if st.checkbox("7. M2M (Watchdog: On / Always On: On)"):
                                if st.checkbox("8. Security (Remote SMS Control: On)"):
                                    step_final_valid = True

    if step_final_valid:
        st.success("✅ Configurações internas validadas.")
        st.divider()
        st.subheader("📡 Testes de Sinal e Hardware")
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            cno_nivel = st.number_input("Nível de Sinal (dBHz)", 0.0, 80.0, 0.0)
            # Lógica visual no Streamlit para o nível de sinal
            if cno_nivel >= 60: st.success(f"Sinal Excelente: {cno_nivel} dBHz")
            elif 53 <= cno_nivel < 60: st.warning(f"Sinal Médio: {cno_nivel} dBHz")
            else: st.error(f"Sinal Insuficiente: {cno_nivel} dBHz")
            
            eth_status = st.selectbox("Porta Ethernet*", ["-", "OK", "Danificada"])
        with col_t2:
            sim_status = st.selectbox("Slot SIM Card*", ["-", "OK", "Mau Contato"])
            real_time = st.selectbox("Real Time (Datalogger)*", ["-", "OK", "FALHA"])
        
        st.divider()
        st.subheader("🎯 Parecer Técnico Final")
        parecer = st.selectbox("Resultado Final*", ["-", "Aprovado para Uso", "Aguardando Manutenção", "Reprovado"])
        ressalvas = st.text_area("Observações Técnicas")

        if st.button("🚀 FINALIZAR E GERAR RELATÓRIO"):
            if "-" in [os_in, serial_in, eth_status, sim_status, real_time, parecer]:
                st.error("🚨 Preencha todos os campos obrigatórios (*)")
            else:
                pdf = PDF_BGAN()
                pdf.add_page()
                
                # Identificação
                pdf.secao_titulo("1. IDENTIFICAÇÃO E CRONOLOGIA")
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(30, 6, "DATA TESTE:"); pdf.set_font('Arial', '', 9); pdf.cell(65, 6, get_br_now().strftime('%d/%m/%Y %H:%M'))
                pdf.set_font('Arial', 'B', 9); pdf.cell(20, 6, "OS:"); pdf.set_font('Arial', '', 9); pdf.cell(75, 6, os_in); pdf.ln()
                pdf.set_font('Arial', 'B', 9); pdf.cell(30, 6, "EQUIPAMENTO:"); pdf.set_font('Arial', '', 9); pdf.cell(65, 6, f"{fab_in} {mod_in}")
                pdf.set_font('Arial', 'B', 9); pdf.cell(20, 6, "S/N:"); pdf.set_font('Arial', '', 9); pdf.cell(75, 6, serial_in); pdf.ln()
                pdf.set_font('Arial', 'B', 9); pdf.cell(30, 6, "OPERADOR:"); pdf.set_font('Arial', '', 9); pdf.cell(160, 6, resp_in); pdf.ln(8)

                pdf.set_font('Arial', 'B', 8); pdf.set_text_color(100, 100, 100)
                pdf.cell(95, 5, f"TEMPO DESDE O PRIMEIRO USO: {dias_desde_primeiro} dias", 0, 0)
                pdf.cell(95, 5, f"TEMPO TOTAL EM ATIVIDADE EM CAMPO: {dias_atividade} dias", 0, 1); pdf.ln(4)

                # Configurações
                pdf.secao_titulo("2. CONFIGURAÇÕES INTERNAS VALIDADAS (WEBUI)")
                pdf.linha_teste("Parâmetros de Conexão e Contextos", "Configurado")
                pdf.linha_teste("Configurações de Ethernet e ATC", "Configurado")
                pdf.linha_teste("M2M Setup e Segurança", "Configurado")
                pdf.ln(4)

                # Resultados com a Nova Lógica de Cores do Sinal
                pdf.secao_titulo("3. RESULTADOS DOS TESTES TÉCNICOS")
                
                # Definindo cor do sinal para o PDF
                if cno_nivel >= 60: cor_sinal = (0, 120, 0)       # Verde
                elif 53 <= cno_nivel < 60: cor_sinal = (255, 140, 0) # Laranja
                else: cor_sinal = (200, 0, 0)                     # Vermelho
                
                pdf.linha_teste("Nível de Sinal (C/No)", f"{cno_nivel} dBHz", cor_custom=cor_sinal)
                pdf.linha_teste("Integridade da Porta Ethernet LAN", eth_status)
                pdf.linha_teste("Integridade do Slot SIM Card", sim_status)
                pdf.linha_teste("Comunicação Real Time com Datalogger", real_time)
                pdf.ln(6)

                # Parecer Final
                pdf.secao_titulo("4. PARECER TÉCNICO FINAL")
                if parecer == "Aprovado para Uso": cor_status = (0, 107, 128)
                elif parecer == "Aguardando Manutenção": cor_status = (255, 140, 0)
                else: cor_status = (200, 0, 0)
                
                pdf.set_text_color(*cor_status); pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, f"STATUS FINAL: {parecer.upper()}", 0, 1, 'C')
                pdf.set_font('Arial', 'I', 9); pdf.set_text_color(0, 0, 0); pdf.ln(2)
                pdf.multi_cell(0, 6, f"Observações: {ressalvas if ressalvas.strip() else 'Nenhuma.'}", border=1)

                try:
                    pdf_output = pdf.output(dest='S')
                    pdf_bytes = bytes(pdf_output) if not isinstance(pdf_output, str) else pdf_output.encode('latin-1')
                    st.download_button(label="⬇️ Baixar Relatório PDF", data=pdf_bytes, file_name=f"Relatorio_BGAN_{serial_in}.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")
