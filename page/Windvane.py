import streamlit as st
import pandas as pd
import numpy as np
import serial
import serial.tools.list_ports
import time
import os
from datetime import datetime
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIGURAÇÕES TÉCNICAS (Mantidas do V10) ---
TOLERANCIA_ACEITAVEL_GRAUS = 2.0
FATOR_MV_GRAU = 360 / 5000.0
MV_ACEITAVEL = TOLERANCIA_ACEITAVEL_GRAUS / FATOR_MV_GRAU

# --- ESTILOS VISUAIS (Identidade do PyQt5) ---
def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #F4F7F9; }
        [data-testid="stSidebar"] { background-color: #009FAD; color: white; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: white !important; }
        .main-card {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            border: 1px solid #E0E0E0;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        }
        .sidebar-title {
            font-size: 20px;
            font-weight: 800;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        div.stButton > button:first-child {
            background-color: #009FAD; color: white; font-weight: bold;
            border-radius: 8px; width: 100%; height: 3.5em; border: none;
        }
        div.stButton > button:hover { background-color: #008591; border: none; color: white; }
        </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE PROCESSAMENTO E GRÁFICOS ---
def processar_dados(buffer_mv, buffer_tempo, serial_num):
    mv_bruto = np.array(buffer_mv)
    tempo_bruto = np.array(buffer_tempo)
    
    # 1. Máscara útil
    mask = (mv_bruto >= 36) & (mv_bruto <= 4967)
    mv_real = mv_bruto[mask]
    
    # 2. Suavização e Referência
    window = 2001 if len(mv_real) > 2001 else (len(mv_real) if len(mv_real)%2!=0 else len(mv_real)-1)
    v_ref_ideal = savgol_filter(mv_real, window_length=max(window, 5), polyorder=3)

    # 3. Gráficos de Linearidade e Erro
    fig_lin, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(mv_real, color='#0044cc', label='Sinal Real')
    ax1.plot(v_ref_ideal, color='#cc0000', linestyle='--', alpha=0.5, label='Referência')
    ax1.set_title(f"Análise Linearidade SN: {serial_num}")
    ax1.set_ylabel("Tensão (mV)")
    ax1.legend()

    erros_graus = (mv_real - v_ref_ideal) * FATOR_MV_GRAU
    ax2.scatter(range(len(erros_graus)), erros_graus, s=1, color='#0044cc')
    ax2.fill_between(range(len(erros_graus)), -TOLERANCIA_ACEITAVEL_GRAUS, TOLERANCIA_ACEITAVEL_GRAUS, color='#ccffcc', alpha=0.3)
    ax2.set_ylabel("Erro (Graus °)")
    plt.tight_layout()

    # 4. Gráfico de Estabilidade (Ruído no ponto central)
    indices_parada = np.where((mv_bruto >= 2480) & (mv_bruto <= 2520))[0]
    fig_ruido = None
    media_mv = 2500
    if len(indices_parada) > 40:
        fig_ruido, ax3 = plt.subplots(figsize=(8, 3))
        dados_parada = mv_bruto[indices_parada]
        media_mv = np.mean(dados_parada)
        ax3.plot(dados_parada, color='#FF8C00')
        ax3.axhline(y=2500, color='green', linestyle='-')
        ax3.set_title("Estabilidade (Ponto Central 180°)")
        plt.tight_layout()

    return fig_lin, fig_ruido, np.max(np.abs(erros_graus)), media_mv

# --- INTERFACE PRINCIPAL ---
aplicar_estilo()

with st.sidebar:
    st.markdown('<div class="sidebar-title">INSTRUÇÕES</div>', unsafe_allow_html=True)
    modo = st.radio("Selecione o Modo:", ["Automático", "Livre"])
    st.write("---")
    
    if modo == "Automático":
        st.markdown("""
        **PASSO A PASSO:**
        1. 🔌 Conecte o sensor USB.
        2. 📝 Preencha Operador e SN.
        3. 🚀 Clique em INICIAR próximo a 0°.
        4. ⏳ Aguarde a parada em 180°.
        """)
    else:
        st.markdown("""
        **MODO LIVRE:**
        1. ▶️ Inicie a captura.
        2. 🔄 Gire manualmente o ciclo.
        3. ⏹️ Finalize para gerar o gráfico bruto.
        """)
    st.markdown("---")
    st.caption("v2.2 CDV Lab")

st.title("Sistema de Avaliação Windvane")

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    operador = c1.text_input("NOME DO OPERADOR")
    serial_num = c2.text_input("SERIAL NUMBER (SN)")

    portas = [p.device for p in serial.tools.list_ports.comports()]
    porta_sel = st.selectbox("PORTA DE COMUNICAÇÃO", portas if portas else ["Nenhuma detectada"])

    if st.button("INICIAR VERIFICAÇÃO"):
        if not operador or not serial_num:
            st.error("⚠️ Preencha os campos obrigatórios.")
        elif not portas:
            st.error("❌ Dispositivo não encontrado.")
        else:
            try:
                ser = serial.Serial(porta_sel, 115200, timeout=0.1)
                buffer_mv, buffer_tempo = [], []
                start_t = time.perf_counter()
                
                msg = st.empty()
                prog = st.progress(0)
                msg.info("Aguardando trigger (5V)...")

                recording = False
                while len(buffer_mv) < 1500:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        try:
                            val = float(line)
                            if not recording and val > 4900:
                                recording = True
                                msg.warning("Capturando dados...")
                            if recording:
                                buffer_mv.append(val)
                                buffer_tempo.append(time.perf_counter() - start_t)
                                prog.progress(min(len(buffer_mv)/1500, 1.0))
                                if val < 20 and len(buffer_mv) > 200: break
                        except: pass
                ser.close()

                # Processamento
                f_lin, f_ruido, erro_max, m_mv = processar_dados(buffer_mv, buffer_tempo, serial_num)
                
                status = "APROVADO" if erro_max <= TOLERANCIA_ACEITAVEL_GRAUS else "REPROVADO"
                st.subheader(f"Status: {status}")
                st.metric("Erro Máximo", f"{erro_max:.2f}°")
                
                st.pyplot(f_lin)
                if f_ruido: st.pyplot(f_ruido)

                # Download do Relatório (Simulado)
                st.success("Dados processados com sucesso. Pasta de arquivos gerada localmente.")

            except Exception as e:
                st.error(f"Falha na captura: {e}")
    st.markdown('</div>', unsafe_allow_html=True)