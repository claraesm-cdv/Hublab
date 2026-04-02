import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Laboratório CDV - Avaliação Datalogger", page_icon="🧪", layout="wide")

# O Hub lê da raiz, então mantemos o nome padrão
DB_FILE = "historico.csv"
# Caminho robusto para a logo na raiz, mesmo rodando de dentro de /pages
LOGO_PATH = os.path.join(os.getcwd(), "logo.png")

# --- CONTROLE DE CRONÔMETRO ---
if 'inicio_sessao' not in st.session_state:
    st.session_state.inicio_sessao = datetime.now()

# --- FUNÇÕES DE BANCO DE DADOS ---
def salvar_no_historico(dados_id, parecer, ressalvas, checklist_detalhado, tempo_execucao):
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    novo_registro = {
        "Data do Teste": data_geracao,
        "Duração do Teste": tempo_execucao,
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
        pdf.cell(0, 10, "EQUIPAMENTO DANIFICADO - NÃO LIGA", 0, 1, 'C')
    else:
        pdf.secao_titulo("2. CHECKLIST DE HARDWARE E SINAIS")
        for grupo in ["Interface Visual", "Sinais e Comunicação", "Energia"]:
            if grupo in checklist_detalhado:
                pdf.set_font('Arial', 'B', 8); pdf.set_text_color(0, 107, 128)
                pdf.cell(0, 6, f"Subgrupo: {grupo}", 0, 1)
                for nome, status in checklist_detalhado[grupo].items():
                    pdf.linha_teste(nome, status)
                pdf.ln(2)

    pdf.secao_titulo("4. PARECER FINAL")
    cor = (0, 120, 0) if parecer == "Aprovado" else (200, 0, 0)
    pdf.set_text_color(*cor); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"STATUS FINAL: {parecer.upper()}", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 9); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, f"Ressalvas: {ressalvas if ressalvas.strip() else 'Nenhuma.'}", border=1)
    
    # O output() da fpdf2 já retorna bytes por padrão
    return pdf.output()

# --- INTERFACE ---
st.title("🧪 Avaliação Datalogger")
tab1, tab2 = st.tabs(["📝 Checklist", "📊 Histórico"])

with tab1:
    c1, c2, c3 = st.columns(3)
    os_in = c1.text_input("OS*")
    serial_in = c1.text_input("Serial*")
    fab_in = c2.text_input("Fabricante*")
    mod_in = c2.text_input("Modelo*")
    resp_in = c3.text_input("Responsável*")
    d_ini = c3.date_input("Entrada", value=datetime.now())
    
    ligando = st.radio("Equipamento liga?*", ["-", "Sim", "Não"], horizontal=True)

    checklist_detalhado = {}
    if ligando == "Sim":
        with st.expander("🔍 Detalhes do Hardware", expanded=True):
            col_a, col_b = st.columns(2)
            leds = col_a.selectbox("LEDs", ["-", "OK", "Não"])
            disp = col_b.selectbox("Display", ["-", "OK", "Não"])
            checklist_detalhado["Interface Visual"] = {"LEDs": leds, "Display": disp}

        st.subheader("Resultado")
        parecer = st.selectbox("Parecer*", ["-", "Aprovado", "Reprovado"])
        ressalvas = st.text_area("Observações")

        if st.button("🚀 FINALIZAR"):
            if not os_in or not serial_in or parecer == "-":
                st.error("Preencha os campos obrigatórios!")
            else:
                agora = datetime.now()
                duracao = agora - st.session_state.inicio_sessao
                tempo_str = f"{duracao.seconds // 60} min"
                
                dados_pdf = {"OS": os_in, "Serial": serial_in, "Fabricante": fab_in, "Modelo": mod_in, "Responsável": resp_in, "Uso": "N/A"}
                salvar_no_historico(dados_pdf, parecer, ressalvas, checklist_detalhado, tempo_str)
                
                # Gerar PDF e garantir que seja BYTES
                pdf_output = gerar_pdf(dados_pdf, parecer, ressalvas, checklist_detalhado, ligando)
                if not isinstance(pdf_output, bytes):
                    pdf_output = bytes(pdf_output)

                st.success("✅ Sucesso!")
                st.download_button("📥 Baixar PDF", data=pdf_output, file_name=f"Relatorio_{serial_in}.pdf", mime="application/pdf")

with tab2:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        st.dataframe(df)
    else:
        st.info("Aguardando primeiro registro...")
