import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="GBS - GPHIDRO BathyScape", page_icon=":ocean:", layout="wide")

def calculate(max_length, min_length, average_depth, sonar_range, sound_speed, beam_width, selected_option):
    try:
        # Verificar e definir valores padrão
        if not beam_width:
            beam_width = 8
        if not sound_speed:
            sound_speed = 1500

        # Cálculo da profundidade dobrada
        double_depth = 2 * sonar_range

        # Cálculo do ping rate
        ping_rate = double_depth / sound_speed
        ping_rate_hz = 1 / ping_rate

        # Cálculo da área
        area = float(max_length * min_length)

        # Cálculo do footprint do sonar
        half_beam_width_radians = np.radians(beam_width / 2)
        sonar_footprint = 2 * average_depth * np.tan(half_beam_width_radians)

        # Cálculo da velocidade de navegação
        velocity_m_s = sonar_footprint * ping_rate_hz
        velocity_knots = velocity_m_s * 1.944

        # Ajustar para a velocidade máxima permitida
        if velocity_knots > 8:
            velocity_knots = 8
            velocity_m_s = 8 / 1.944

        # Recalcular o ping rate considerando a velocidade de navegação e a cobertura desejada
        ping_rate_hz = velocity_m_s / sonar_footprint
        if ping_rate_hz > 20:
            ping_rate_hz = 20
            velocity_m_s = sonar_footprint * ping_rate_hz
            velocity_knots = velocity_m_s * 1.944

        # Cálculo dos espaçamentos das linhas e do tempo de levantamento
        reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines = \
            line_spacing(area, max_length, min_length, selected_option, average_depth)

        survey_time_minutes = ((total_reg_lines * min_length + total_cross_lines * max_length) / velocity_m_s) / 60
        survey_time_rounded = round(survey_time_minutes)
        unit = 'minutos'

        if survey_time_rounded >= 60:
            survey_time_rounded = round(survey_time_rounded / 60)
            unit = 'horas'
        total_time = round(survey_time_rounded * 1.25)

        # Resultados
        results = {
            'Área total do levantamento': f'{area:.2f} m²',
            'Ping Rate Máximo recomendado': f'{ping_rate_hz:.2f} Hertz',
            'Espaçamento das linhas regulares de sondagem': f'{reg_line_spacing:.2f} m',
            'Espaçamento das linhas de verificação': f'{cross_line_spacing:.2f} m',
            'Tempo estimado para levantamento das linhas': f'{survey_time_rounded:.1f} {unit}',
            'Tempo total estimado para o levantamento': f'{total_time:.1f} {unit}',
            'Velocidade de navegação recomendada para uma cobertura de 100%': f'{velocity_knots:.2f} nós'
        }

        now = datetime.now()
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")

        pdf_file = generate_pdf_report(results, title="Relatório de Planejamento de Campanha Batimétrica", date=date,
                                       time=time)
        return results, sonar_footprint, pdf_file

    except ValueError:
        st.error("Por favor, insira valores válidos.")
        return None, None, None


def line_spacing(area, max_length, min_length, selected_option, average_depth):
    km = max_length / 1000
    if selected_option == 'Normam':
        reg_line_spacing = min(3 * average_depth, 25)
        cross_line_spacing = 10 * reg_line_spacing

    elif selected_option == 'ANA-UHE':
        hectares = area / 10000
        reg_line_spacing = (0.35 * (hectares ** 0.35)) / km
        cross_line_spacing = 3 * reg_line_spacing

    elif selected_option == 'ANA-PCH':
        hectares = area / 10000
        reg_line_spacing = (0.1 * (hectares ** 0.25)) / km
        cross_line_spacing = 3 * reg_line_spacing

    if cross_line_spacing >= min_length:
        cross_line_spacing = min_length / 2

    total_reg_lines = round(max_length / reg_line_spacing)
    total_cross_lines = round(min_length / cross_line_spacing)

    return reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines

def draw_footprint():
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    diameter = 15
    spacing = 0

    for i in range(5):
        circle = plt.Circle((10 + i * (diameter + spacing), 50), diameter/2, edgecolor='lightblue', facecolor='none',
                            lw=1)
        ax.add_patch(circle)

    ax.set_xlim(0, 50 + 5 * (diameter + spacing))
    ax.set_ylim(0, 100)
    ax.set_aspect('equal', 'box')
    ax.axis('off')
    ax.text(10 + diameter / 2, 50 + diameter + 10, "Pegada do sonar", ha='center', va='center', fontsize=14,
            fontweight='bold', color='white')

    st.pyplot(fig)

def generate_pdf_report(results, title="Relatório de Resultados", date=None, time=None):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setTitle(title)

    x_start = 50
    y_start = 750
    line_height = 20

    c.setFont("Helvetica", 12)
    c.drawString(x_start, y_start, f"{title}: GBS - GPHIDRO BathyScape")
    y_start -= line_height

    if date:
        c.drawString(x_start, y_start, f"Data: {date}")
        y_start -= line_height

    if time:
        c.drawString(x_start, y_start, f"Hora: {time}")
        y_start -= line_height

    c.drawString(x_start, y_start, "Resultados:")
    y_start -= line_height * 2

    for key, value in results.items():
        text = f"{key}: {value}"
        c.drawString(x_start, y_start, text)
        y_start -= line_height

    c.save()

    # Retornar os bytes do PDF gerado
    return buffer.getvalue()

st.title("GBS - GPHIDRO BathyScape")
st.write("Planejamento de campanhas batimétricas")

col1, col2 = st.columns(2)
with col1:
    max_length = st.number_input("Comprimento máximo da área (m):", min_value=0.0, step=5.0,
                                 help='Comprimento da maior feição da área')
    min_length = st.number_input("Comprimento mínimo da área (m):", min_value=0.0, step=5.0,
                                 help='Comprimento da menor feição da área')
    average_depth = st.number_input("Profundidade média da área (m):", min_value=0.0, step=5.0,
                                    help='Profundidade média estimada da área')
    sonar_range = st.number_input("Alcance do sonar (m):", min_value=0.0, step=5.0,
                                  help='Alcance configurado do sonar em metros')

with col2:
    sound_speed = st.number_input("Velocidade do som na água (m/s):", min_value=0.0, value=1500.0,
                                  help='Velocidade média obtida do som na água')
    beam_width = st.number_input("Largura de feixe (graus):", min_value=0.0, value=8.0,
                                 help='Largura de feixe do sonar em graus')
    selected_option = st.radio("Selecione a norma:", ["Normam", "ANA-UHE", "ANA-PCH"],
                               help='Selecione a norma que deseja seguir.')

if st.button("Calcular"):
    results, sonar_footprint, pdf_file = calculate(max_length, min_length, average_depth, sonar_range, sound_speed,
                                         beam_width, selected_option)
    if results:
        st.write("Resultados do cálculo:")
        for key, value in results.items():
            st.write(f"{key}: {value}")

        # Exibir o gráfico das pegadas do sonar
        pdf_file = generate_pdf_report(results)
        draw_footprint()

# Menu lateral com opções de ajuda, sobre e download do relatório PDF
st.sidebar.title("Menu")
if st.sidebar.button("Ajuda"):
    st.info(
        "Para calcular o planejamento de campanhas batimétricas, insira os dados solicitados e clique em 'Calcular'.\n\n"
        "Comprimento máximo e mínimo da área (m): Comprimento das feições da área a ser levantada.\n\n"
        "Profundidade média da área (m): Profundidade média estimada da área a ser levantada, em metros.\n\n"
        "Alcance do sonar (m): Alcance configurado do sonar em metros.\n\n"
        "Velocidade do som na água (m/s): Insira a velocidade média obtida do som na água, em m/s.\n\n"
        "Largura de feixe (graus): Insira a largura de feixe do seu sonar, em graus.\n\n"
        "Selecione a norma: Selecione a norma que deseja seguir."
    )

if st.sidebar.button("Sobre"):
    st.info(
        "Software para planejamento de campanhas batimétricas desenvolvido por Lucas Costa - lucas.h.costa@ufv.br\n"
        "GPHIDRO (Grupo de Pesquisa em Hidrografia)\nVersão 1.1"
    )

# Botão de download do relatório PDF
if 'pdf_file' in locals():
    st.sidebar.download_button(
        label="Clique aqui para baixar o relatório",
        data=pdf_file,
        file_name="relatorio_resultados.pdf",
        mime="application/pdf"
    )
