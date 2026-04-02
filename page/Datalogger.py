import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Laboratório CDV - Avaliação Datalogger", page_icon="🧪", layout="wide")

DB_FILE = "historico.csv"
LOGO_PATH = "logo.png"

# --- CONTROLE DE CRONÔMETRO (TEMPO DE TESTE - APENAS PARA BD) ---
if 'inicio_sessao' not in st.session_state:
    st.session_state.inicio_sessao = datetime.now()

# --- FUNÇÕES DE BANCO DE DADOS ---
def salvar_no_historico(dados_id, parecer, ressalvas, checklist_detalhado, tempo_execucao):
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    novo_registro = {
        "Data do Teste": data_geracao,
        "Duração do Teste": tempo_execucao, # Salva no CSV
        "OS": str(dados_id.get("OS", "")),
        "Serial": str(dados_id.get("Serial", "")),
        "Fabricante": str(dados_id.get("Fabricante", "")),
        "Modelo": str(dados_id.get("Modelo", "")),
        "Responsável": str(dados_id.get("Responsável", "")),
        "Dias de Uso": str(dados_id.get("Uso", "")),
        "Parecer": parecer,
        "Ressalvas": ressalvas
    }
    for grupo in checklist_detalhado.values():
        novo_registro.update(grupo)
    
    df_novo = pd.DataFrame([novo_registro])
    if os.path.exists(DB_FILE):
        df_antigo = pd.read_csv(DB_FILE)
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
    else:
        df_final = df_novo
    df_final.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def excluir_registro_por_data(data_hora):
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df = df[df['Data do Teste'] != data_hora]
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        return True
    return False

# --- CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 107, 128)
        self.cell(190, 10, 'RELATÓRIO DE INSPEÇÃO TÉCNICA', 0, 1, 'R')
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
        self.cell(largura * 0.8, 5, f"  > {nome}", 0, 0, 'L')
        
        status_positivos = ["OK", "Aprovado", "Cartao SD", "Cartao microSD"]
        if status in status_positivos:
            self.set_text_color(0, 120, 0)
            self.cell(largura * 0.2, 5, f"[ {status} ]", 0, 1, 'R')
        else:
            self.set_text_color(200, 0, 0)
            self.cell(largura * 0.2, 5, "[ FALHA ]", 0, 1, 'R')
        self.set_text_color(0, 0, 0)

def gerar_pdf(dados_id, parecer, ressalvas, checklist_detalhado, ligando):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    # 1. IDENTIFICAÇÃO
    pdf.secao_titulo("1. IDENTIFICAÇÃO DO DATALOGGER")
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(25, 6, "OS:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["OS"]), 0)
    pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Serial:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["Serial"]), 0); pdf.ln()
    pdf.cell(25, 6, "Fabricante:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["Fabricante"]), 0)
    pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Modelo:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["Modelo"]), 0); pdf.ln()
    pdf.cell(25, 6, "Responsável:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["Responsável"]), 0)
    pdf.set_font('Arial', 'B', 9); pdf.cell(25, 6, "Uso:", 0); pdf.set_font('Arial', '', 9); pdf.cell(70, 6, str(dados_id["Uso"]), 0); pdf.ln()
    pdf.ln(4)
    
    if ligando == "Não":
        pdf.secao_titulo("2. STATUS DE INICIALIZAÇÃO")
        pdf.set_font('Arial', 'B', 12); pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, "EQUIPAMENTO DANIFICADO - NÃO INICIALIZA / NÃO LIGA", 0, 1, 'C')
        pdf.ln(5)
    else:
        # 2. CHECKLIST GERAL
        pdf.secao_titulo("2. CHECKLIST DE HARDWARE E SINAIS")
        for grupo in ["Interface Visual", "Sinais e Comunicação", "Energia"]:
            if grupo in checklist_detalhado:
                pdf.set_font('Arial', 'B', 8); pdf.set_text_color(0, 107, 128)
                pdf.cell(0, 6, f"Subgrupo: {grupo}", 0, 1)
                for nome, status in checklist_detalhado[grupo].items():
                    pdf.linha_teste(nome, status)
                pdf.ln(2)

        # 3. CANAIS
        pdf.secao_titulo("3. MAPEAMENTO DE CANAIS DE ENTRADA")
        y_topo = pdf.get_y()
        pdf.set_font('Arial', 'B', 8); pdf.set_text_color(0, 107, 128); pdf.cell(95, 5, "Analógicas", 0, 1)
        for nome, status in checklist_detalhado.get("Entradas Analógicas", {}).items():
            pdf.linha_teste(nome, status, 92)
        y_fim_anl = pdf.get_y()
        
        pdf.set_xy(108, y_topo)
        pdf.set_font('Arial', 'B', 8); pdf.set_text_color(0, 107, 128); pdf.cell(95, 5, "Frequência", 0, 1)
        for nome, status in checklist_detalhado.get("Entradas Frequência", {}).items():
            pdf.set_x(108); pdf.linha_teste(nome, status, 92)
        pdf.set_y(max(y_fim_anl, pdf.get_y()) + 4)

    # 4. PARECER
    pdf.secao_titulo("4. PARECER FINAL")
    cor = (0, 120, 0) if parecer == "Aprovado" else (200, 0, 0)
    pdf.set_text_color(*cor); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"STATUS FINAL: {parecer.upper()}", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 9); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, f"Ressalvas: {ressalvas if ressalvas.strip() else 'Nenhuma.'}", border=1)
    
    return bytes(pdf.output())

# --- INTERFACE ---
st.title("🧪 Laboratório CDV - Avaliação Datalogger")
tab1, tab2 = st.tabs(["📝 Novo Checklist", "📊 Banco de Dados"])

with tab1:
    st.subheader("1. Identificação")
    c1, c2, c3 = st.columns(3)
    os_in = c1.text_input("OS*")
    serial_in = c1.text_input("Serial*")
    fab_in = c2.text_input("Fabricante*")
    mod_in = c2.text_input("Modelo*")
    resp_in = c3.text_input("Responsável*")
    
    c_dat1, c_dat2 = c3.columns(2)
    d_ini = c_dat1.date_input("Entrada", value=datetime.now())
    d_fim = c_dat2.date_input("Saída", value=datetime.now())
    dias_calc = (d_fim - d_ini).days
    st.info(f"⏳ **Permanência:** {dias_calc} dias")

    st.divider()
    ligando = st.radio("Equipamento liga?*", ["-", "Sim", "Não"], horizontal=True)

    checklist_detalhado = {}
    parecer = "-"
    ressalvas = ""

    if ligando == "Sim":
        st.subheader("2. Inspeção Detalhada")
        
        with st.expander("🖥️ Interface Visual", expanded=True):
            col_iv1, col_iv2, col_iv3 = st.columns(3)
            leds = col_iv1.selectbox("LEDs*", ["-", "OK", "Não"], format_func=lambda x: "OK" if x=="OK" else ("FALHA" if x=="Não" else x))
            disp = col_iv2.selectbox("Display*", ["-", "OK", "Não"], format_func=lambda x: "OK" if x=="OK" else ("FALHA" if x=="Não" else x))
            grav = col_iv3.selectbox("Gravação Interna*", ["-", "Cartao SD", "Cartao microSD"])
            
            checklist_detalhado["Interface Visual"] = {
                "LEDs": "OK" if leds == "OK" else ("FALHA" if leds == "Não" else "-"),
                "Display": "OK" if disp == "OK" else ("FALHA" if disp == "Não" else "-"),
                "Gravação": grav
            }

        with st.expander("📡 Sinais e Comunicação"):
            cs1, cs2, cs3, cs4 = st.columns(4)
            gsm = cs1.selectbox("GSM*", ["-", "OK", "Não"], format_func=lambda x: "OK" if x=="OK" else ("FALHA" if x=="Não" else x))
            gps = cs2.selectbox("GPS*", ["-", "OK", "Não"], format_func=lambda x: "OK" if x=="OK" else ("FALHA" if x=="Não" else x))
            moxa = cs3.selectbox("MOXA*", ["-", "OK", "Não"], format_func=lambda x: "OK" if x=="OK" else ("FALHA" if x=="Não" else x))
            rt = cs4.selectbox("Real Time*", ["-", "OK", "Não"], format_func=lambda x: "OK" if x=="OK" else ("FALHA" if x=="Não" else x))
            
            checklist_detalhado["Sinais e Comunicação"] = {
                "GSM": "OK" if gsm == "OK" else ("FALHA" if gsm == "Não" else "-"),
                "GPS": "OK" if gps == "OK" else ("FALHA" if gps == "Não" else "-"),
                "MOXA": "OK" if moxa == "OK" else ("FALHA" if moxa == "Não" else "-"),
                "Real Time": "OK" if rt == "OK" else ("FALHA" if rt == "Não" else "-")
            }

        with st.expander("🔌 Energia"):
            cv1, cv2, cv3 = st.columns(3)
            v12 = cv1.selectbox("12V*", ["-", "OK", "Não"], format_func=lambda x: "OK" if x=="OK" else ("FALHA" if x=="Não" else x))
            v5 = cv2.selectbox("5V*", ["-", "OK", "Não"], format_func=lambda x: "OK" if x=="OK" else ("FALHA" if x=="Não" else x))
            v25 = cv3.selectbox("2,5V*", ["-", "OK", "Não"], format_func=lambda x: "OK" if x=="OK" else ("FALHA" if x=="Não" else x))
            
            checklist_detalhado["Energia"] = {
                "12V": "OK" if v12 == "OK" else ("FALHA" if v12 == "Não" else "-"),
                "5V": "OK" if v5 == "OK" else ("FALHA" if v5 == "Não" else "-"),
                "2.5V": "OK" if v25 == "OK" else ("FALHA" if v25 == "Não" else "-")
            }

        cio1, cio2 = st.columns(2)
        with cio1:
            with st.expander("🛠️ Analógicas"):
                st_anl = {}
                cols_an = st.columns(3)
                for i in range(1, 16):
                    st_anl[f"ANL {i}"] = "OK" if cols_an[(i-1)%3].checkbox(f"ANL {i}", value=True) else "FALHA"
                checklist_detalhado["Entradas Analógicas"] = st_anl
        with cio2:
            with st.expander("⚡ Frequência"):
                st_frq = {}
                cols_fr = st.columns(2)
                for i in range(1, 11):
                    st_frq[f"FREQ {i}"] = "OK" if cols_fr[(i-1)%2].checkbox(f"FREQ {i}", value=True) else "FALHA"
                checklist_detalhado["Entradas Frequência"] = st_frq

        st.subheader("3. Parecer")
        parecer = st.selectbox("Resultado Final*", ["-", "Aprovado", "Reprovado", "Aprovado com Ressalvas"])
        ressalvas = st.text_area("Observações")

    elif ligando == "Não":
        st.error("⚠️ Equipamento não inicializa.")
        parecer = "Reprovado"
        ressalvas = st.text_area("Observações Adicionais", value="Equipamento danificado e não inicializa.")
        checklist_detalhado = {"Status": {"Geral": "FALHA"}}

    if ligando != "-":
        if st.button("🚀 FINALIZAR"):
            erro = False
            if not os_in or not serial_in:
                st.error("🚨 OS e Serial são obrigatórios!")
                erro = True
            
            if ligando == "Sim":
                flat_list = [v for g in checklist_detalhado.values() for v in g.values()]
                if "-" in flat_list or parecer == "-":
                    st.error("🚨 Preencha todos os campos da inspeção detalhada!")
                    erro = True

            if not erro:
                # Cálculo do tempo (mm:ss) apenas para o BD
                agora = datetime.now()
                duracao = agora - st.session_state.inicio_sessao
                minutos, segundos = divmod(duracao.seconds, 60)
                tempo_str = f"{minutos:02d}:{segundos:02d} min"

                dados_pdf = {"OS": os_in, "Serial": serial_in, "Fabricante": fab_in, "Modelo": mod_in, "Responsável": resp_in, "Uso": f"{dias_calc} dias"}
                
                # Salva no histórico (CSV) incluindo o tempo
                salvar_no_historico(dados_pdf, parecer, ressalvas, checklist_detalhado, tempo_str)
                
                # Gera o PDF (o tempo não é passado para a função gerar_pdf)
                fname = f"{datetime.now().strftime('%d%m%y')}_DL{serial_in}.pdf"
                pdf_bytes = gerar_pdf(dados_pdf, parecer, ressalvas, checklist_detalhado, ligando)
                
                st.success(f"✅ Relatório Gerado com Sucesso!")
                st.download_button("📥 Baixar PDF", pdf_bytes, fname, mime="application/pdf")
                
                # Reseta o cronômetro para o próximo teste
                st.session_state.inicio_sessao = datetime.now()

with tab2:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        st.dataframe(df, use_container_width=True)
        
        st.subheader("🗑️ Apagar Registro")
        op_del = df["Data do Teste"].tolist()
        sel_del = st.selectbox("Selecione pela Data/Hora:", options=op_del)
        if st.button("Confirmar Exclusão", type="primary"):
            if excluir_registro_por_data(sel_del): st.rerun()
    else: st.info("Sem dados.")
