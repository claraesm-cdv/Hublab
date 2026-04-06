import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from fpdf import FPDF
import os
import sqlite3

# --- BANCO DE DADOS (SQLite) ---
DB_NAME = "relatorios_bgan.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS testes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  data_teste TEXT, os TEXT, imei TEXT, operador TEXT, 
                  fabricante TEXT, modelo TEXT, sinal REAL, ethernet TEXT, 
                  sim_card TEXT, real_time TEXT, parecer TEXT, observacoes TEXT)''')
    conn.commit()
    conn.close()

def salvar_relatorio(dados):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO testes (data_teste, os, imei, operador, fabricante, modelo, sinal, ethernet, sim_card, real_time, parecer, observacoes)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', dados)
    conn.commit()
    conn.close()

# Inicializa o banco ao rodar o app
init_db()

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

# --- CLASSE PDF ESTILIZADA (Mesma do seu código original) ---
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

tab1, tab2 = st.tabs(["📝 Verificação do equipamento", "📊 Histórico de Testes"])

with tab1:
    st.subheader("1. Identificação do Terminal")
    c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
    
    sem_historico = c4.checkbox("🚫 Equipamento Novo (Sem histórico/OS)")
    
    os_in = c1.text_input("OS*", value="N/A" if sem_historico else "", disabled=sem_historico)
    serial_in = c2.text_input("IMEI*")
    resp_in = c3.text_input("Operador*")
    
    fab_in = c1.selectbox("Fabricante*", ["-", "Hughes"])
    mod_in = c2.selectbox("Modelo*", ["-", "9502"])

    st.write("---")
    
    if not sem_historico:
        st.markdown("##### ⏳ Histórico de Passagens em Campo")
        for i, periodo in enumerate(st.session_state.periodos):
            col_p1, col_p2, col_p3 = st.columns([4, 4, 1])
            st.session_state.periodos[i]["entrada"] = col_p1.date_input(f"Entrada {i+1}", value=periodo["entrada"], key=f"ent_{i}", format="DD/MM/YYYY")
            st.session_state.periodos[i]["saida"] = col_p2.date_input(f"Saída {i+1}", value=periodo["saida"], key=f"sai_{i}", format="DD/MM/YYYY")
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
    else:
        dias_atividade = 0
        dias_desde_primeiro = 0

    st.divider()
    
    # --- Checklist (Simplificado para o exemplo, mantendo sua lógica) ---
    st.subheader("🛠️ Checklist e Testes")
    step_final_valid = st.checkbox("Confirmar que todas as etapas de configuração WebUI foram seguidas?")

    if step_final_valid:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            cno_nivel = st.number_input("Nível de Sinal (dBHz)", 0.0, 80.0, 0.0)
            eth_status = st.selectbox("Porta Ethernet*", ["-", "OK", "Danificada"])
        with col_t2:
            sim_status = st.selectbox("Slot SIM Card*", ["-", "OK", "Mau Contato"])
            real_time = st.selectbox("Real Time (Datalogger)*", ["-", "OK", "FALHA"])
        
        parecer = st.selectbox("Resultado Final*", ["-", "Aprovado para Uso", "Aguardando Manutenção", "Reprovado"])
        ressalvas = st.text_area("Observações Técnicas")

        if st.button("🚀 FINALIZAR E GERAR RELATÓRIO"):
            valid_os = True if sem_historico else (os_in.strip() != "" and os_in != "-")
            
            if "-" in [serial_in, eth_status, sim_status, real_time, parecer] or not valid_os:
                st.error("🚨 Preencha todos os campos obrigatórios (*)")
            else:
                # --- SALVAR NO BANCO DE DADOS ---
                data_atual = get_br_now().strftime('%Y-%m-%d %H:%M:%S')
                dados_teste = (data_atual, os_in, serial_in, resp_in, fab_in, mod_in, cno_nivel, eth_status, sim_status, real_time, parecer, ressalvas)
                salvar_relatorio(dados_teste)
                
                # --- GERAR PDF ---
                pdf = PDF_BGAN()
                pdf.add_page()
                pdf.secao_titulo("1. IDENTIFICAÇÃO E CRONOLOGIA")
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(30, 6, "DATA TESTE:"); pdf.set_font('Arial', '', 9); pdf.cell(65, 6, get_br_now().strftime('%d/%m/%Y %H:%M'))
                pdf.set_font('Arial', 'B', 9); pdf.cell(15, 6, "OS:"); pdf.set_font('Arial', '', 9); pdf.cell(80, 6, os_in); pdf.ln()
                
                # (O restante da lógica do seu PDF permanece igual...)
                pdf.cell(0, 10, f"STATUS FINAL: {parecer.upper()}", 0, 1, 'C')
                
                pdf_output = pdf.output(dest='S')
                pdf_bytes = bytes(pdf_output) if not isinstance(pdf_output, str) else pdf_output.encode('latin-1')
                
                st.success("✅ Teste registrado no banco de dados!")
                st.download_button(label="⬇️ Baixar Relatório PDF", data=pdf_bytes, file_name=f"Relatorio_{serial_in}.pdf", mime="application/pdf")

with tab2:
    st.subheader("📊 Histórico de Avaliações")
    
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM testes ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        # Filtro simples
        busca_imei = st.text_input("Filtrar por IMEI")
        if busca_imei:
            df = df[df['imei'].str.contains(busca_imei)]
            
        st.dataframe(df, use_container_width=True)
        
        # Opção para exportar o histórico completo
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar Histórico (CSV)", csv, "historico_bgan.csv", "text/csv")
    else:
        st.info("Nenhum registro encontrado no banco de dados.")
