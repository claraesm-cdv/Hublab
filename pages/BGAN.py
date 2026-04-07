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

def salvar_no_banco(dados):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO testes (data_teste, os, imei, operador, fabricante, modelo, sinal, ethernet, sim_card, real_time, parecer, observacoes)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', dados)
    conn.commit()
    conn.close()

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
    
    c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
    
    sem_historico = c4.checkbox("🚫 Equipamento Novo (Sem histórico/OS)")
    
    os_in = c1.text_input("OS*", value="N/A" if sem_historico else "", disabled=sem_historico)
    serial_in = c2.text_input("IMEI*")
    resp_in = c3.text_input("Operador*")
    
    fab_in = c1.selectbox("Fabricante*", ["-", "Hughes"])
    mod_in = c2.selectbox("Modelo*", ["-", "9502"])

    st.write("---")
    
    # --- LOGICA DOS CONTADORES (PRESERVADA) ---
    dias_atividade = 0
    dias_desde_primeiro = 0

    if not sem_historico:
        st.markdown("##### ⏳ Histórico de Passagens em Campo")
        
        for i, periodo in enumerate(st.session_state.periodos):
            col_p1, col_p2, col_p3 = st.columns([4, 4, 1])
            st.session_state.periodos[i]["entrada"] = col_p1.date_input(f"Entrada {i+1}", value=periodo["entrada"], key=f"ent_{i}", format="DD/MM/YYYY")
            st.session_state.periodos[i]["saida"] = col_p2.date_input(f"Saída {i+1}", value=periodo["saida"], key=f"sai_{i}", format="DD/MM/YYYY")
            if len(st.session_state.periodos) > i: # Garante que o índice existe
                if col_p3.button("🗑️", key=f"del_{i}"):
                    st.session_state.periodos.pop(i)
                    st.rerun()

        if st.button("➕ Adicionar Passagem"):
            st.session_state.periodos.append({"entrada": get_br_now().date(), "saida": get_br_now().date()})
            st.rerun()

        if st.session_state.periodos:
            dias_atividade = sum([(p["saida"] - p["entrada"]).days for p in st.session_state.periodos])
            primeira_entrada = min([p["entrada"] for p in st.session_state.periodos])
            dias_desde_primeiro = (get_br_now().date() - primeira_entrada).days
    else:
        st.info("💡 **Aviso:** Modo 'Equipamento Novo' ativo. O histórico de campo será omitido do relatório.")

    # Exibição das métricas (Exatamente como no original)
    c_res1, c_res2 = st.columns(2)
    c_res1.metric("Tempo desde 1º uso", f"{dias_desde_primeiro} dias")
    c_res2.metric("Tempo total em atividade", f"{dias_atividade} dias")

    st.divider()
    st.subheader("🛠️ Checklist de Configuração Sequencial")

    step_final_valid = False

    s0 = st.checkbox("0. Modo Avião do computador ligado?")
    if s0:
        st.markdown("---")
        st.info("💡 **Instrução:** Conecte o Cabo RJ45 e Vá em Painel de Controle > Rede e Internet > Conexões de Rede")
        s1 = st.checkbox("1. Protocolo TCP/IP: IP e DNS em modo automático?")
        if s1:
            st.markdown("---")
            st.info("🔗 **Acesse o WebUI:** http://192.168.128.100")
            s2 = st.checkbox("2. Página inicial do equipamento carregada?")
            if s2:
                st.markdown("---")
                st.warning("⚙️ **Configuração:** Connections > Manage Contexts")
                st.write("- Owner: 192.168.128.101 | Service: Standard | APN: STRATOS ou WILTD")
                s3 = st.checkbox("3. Configurações de Contexto conferidas?")
                if s3:
                    st.markdown("---")
                    st.warning("⚙️ **Configuração:** Connections > Automatic Contexts")
                    st.write("- Static IP ACA: 1 | Enable: Off | Service: Standard")
                    s4 = st.checkbox("4. Contexto Automático conferido?")
                    if s4:
                        st.markdown("---")
                        st.warning("⚙️ **Configuração:** Settings > Ethernet")
                        st.write("- Wake On LAN: Off | Idle Timeout: 0 | Ethernet: Default")
                        s5 = st.checkbox("5. Configurações de Ethernet conferidas?")
                        if s5:
                            st.markdown("---")
                            st.warning("⚙️ **Configuração:** Settings > ATC Setup")
                            st.write("- ATC Robustness: Off")
                            s6 = st.checkbox("6. ATC Setup conferido?")
                            if s6:
                                st.markdown("---")
                                st.warning("⚙️ **Configuração:** Settings > M2M")
                                st.write("- Watchdog: On (8.8.8.8) | Always On: On (192.168.128.101)")
                                s7 = st.checkbox("7. Watchdog e Always On configurados?")
                                if s7:
                                    st.markdown("---")
                                    st.warning("⚙️ **Configuração:** Settings > Security")
                                    st.write("- Remote SMS Control: On | Password: remote")
                                    if st.checkbox("8. Configurações de Segurança finalizadas?"):
                                        st.markdown("---")
                                        st.warning(" 🚨 Desconete o modem BGAN do computador, conecte-o ao MOXA e retire o computador do modo avião ")
                                        step_final_valid = True

    if step_final_valid:
        st.success("✅ Todas as configurações internas foram validadas.")
        st.divider()
        st.subheader("📡 Testes de Sinal e Hardware")
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            cno_nivel = st.number_input("Nível de Sinal (dBHz)", 0.0, 80.0, 0.0)
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
            valid_os = True if sem_historico else (os_in.strip() != "" and os_in != "-")
            
            if "-" in [serial_in, eth_status, sim_status, real_time, parecer] or not valid_os:
                st.error("🚨 Preencha todos os campos obrigatórios (*)")
            else:
                # --- SALVAR DADOS NO SQLITE ---
                data_db = get_br_now().strftime('%Y-%m-%d %H:%M:%S')
                dados_para_salvar = (data_db, os_in, serial_in, resp_in, fab_in, mod_in, cno_nivel, eth_status, sim_status, real_time, parecer, ressalvas)
                salvar_no_banco(dados_para_salvar)

                # --- GERAR PDF ---
                pdf = PDF_BGAN()
                pdf.add_page()
                pdf.secao_titulo("1. IDENTIFICAÇÃO E CRONOLOGIA")
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(30, 6, "DATA TESTE:"); pdf.set_font('Arial', '', 9); pdf.cell(65, 6, get_br_now().strftime('%d/%m/%Y %H:%M'))
                pdf.set_font('Arial', 'B', 9); pdf.cell(15, 6, "OS:"); pdf.set_font('Arial', '', 9); pdf.cell(80, 6, os_in); pdf.ln()
                pdf.set_font('Arial', 'B', 9); pdf.cell(30, 6, "FABRICANTE:"); pdf.set_font('Arial', '', 9); pdf.cell(65, 6, fab_in)
                pdf.set_font('Arial', 'B', 9); pdf.cell(20, 6, "MODELO:"); pdf.set_font('Arial', '', 9); pdf.cell(75, 6, mod_in); pdf.ln()
                pdf.set_font('Arial', 'B', 9); pdf.cell(30, 6, "IMEI:"); pdf.set_font('Arial', '', 9); pdf.cell(65, 6, serial_in)
                pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "OPERADOR:"); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, resp_in); pdf.ln(8)

                pdf.set_font('Arial', 'B', 8); pdf.set_text_color(100, 100, 100)
                if sem_historico:
                    pdf.cell(190, 5, "INSTRUMENTO SEM HISTÓRICO DE INSTALAÇÃO (EQUIPAMENTO NOVO)", 0, 1)
                else:
                    pdf.cell(95, 5, f"TEMPO DESDE O PRIMEIRO USO: {dias_desde_primeiro} dias", 0, 0)
                    pdf.cell(95, 5, f"TEMPO TOTAL EM ATIVIDADE EM CAMPO: {dias_atividade} dias", 0, 1)
                pdf.ln(4)

                pdf.secao_titulo("2. CONFIGURAÇÕES INTERNAS VALIDADAS (WEBUI)")
                pdf.linha_teste("Modo Avião do Host e TCP/IP", "OK")
                pdf.linha_teste("Conexão WebUI e Contextos", "Configurado")
                pdf.linha_teste("Ethernet, ATC e M2M Setup", "Configurado")
                pdf.linha_teste("Security e Remote SMS Control", "Configurado")
                pdf.ln(4)

                pdf.secao_titulo("3. RESULTADOS DOS TESTES TÉCNICOS")
                if cno_nivel >= 60: cor_sinal = (0, 120, 0)
                elif 53 <= cno_nivel < 60: cor_sinal = (255, 140, 0)
                else: cor_sinal = (200, 0, 0)
                pdf.linha_teste("Nível de Sinal (C/No)", f"{cno_nivel} dBHz", cor_custom=cor_sinal)
                pdf.linha_teste("Integridade da Porta Ethernet LAN", eth_status)
                pdf.linha_teste("Integridade do Slot SIM Card", sim_status)
                pdf.linha_teste("Comunicação Real Time com Datalogger", real_time)
                pdf.ln(6)

                pdf.secao_titulo("4. PARECER TÉCNICO FINAL")
                if parecer == "Aprovado para Uso": cor_status = (0, 107, 128)
                elif parecer == "Aguardando Manutenção": cor_status = (255, 140, 0)
                else: cor_status = (200, 0, 0)
                pdf.set_text_color(*cor_status); pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, f"STATUS FINAL: {parecer.upper()}", 0, 1, 'C')
                pdf.set_font('Arial', 'I', 9); pdf.set_text_color(0, 0, 0); pdf.ln(2)
                pdf.multi_cell(0, 6, f"Observações: {ressalvas if ressalvas.strip() else 'Nenhuma.'}", border=1)

                data_str = get_br_now().strftime("%d%m%Y")
                pdf_filename = f"{data_str}_BGAN_{serial_in}.pdf"

                try:
                    pdf_output = pdf.output(dest='S')
                    pdf_bytes = bytes(pdf_output) if not isinstance(pdf_output, str) else pdf_output.encode('latin-1')
                    st.success("✅ Relatório salvo no histórico com sucesso!")
                    st.download_button(label="⬇️ Baixar Relatório PDF", data=pdf_bytes, file_name=pdf_filename, mime="application/pdf")
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")

with tab2:
    st.subheader("📊 Histórico de Registros")
    conn = sqlite3.connect(DB_NAME)
    # Lê todos os dados do banco
    df = pd.read_sql_query("SELECT id, data_teste as 'Data', os as 'OS', imei as 'IMEI', operador as 'Operador', parecer as 'Status Final' FROM testes ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        # Botão para baixar a planilha completa
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Planilha de Histórico (CSV)", csv, "historico_bgan.csv", "text/csv")
    else:
        st.info("Nenhum registro encontrado no banco de dados.")
