import numpy as np
import streamlit as st
import functions as f
import tempfile

st.set_page_config(page_title="GBS - GPHIDRO BathyScape", page_icon=":ocean:", layout="wide")

def calculate(max_length, min_length, average_depth, sonar_range, sound_speed, beam_width, selected_option):
    try:
        # defining standard values
        if not beam_width:
            beam_width = 8
        if not sound_speed:
            sound_speed = 1500
        if not average_depth:
            average_depth = 10
        if not max_length:
            max_length = 1000
        if not min_length:
            min_length = 100
        if not sonar_range:
            sonar_range = 10

        # Calculating double range
        double_depth = 2 * sonar_range

        # actual ping rate calculation
        ping_rate = double_depth / sound_speed  # CHANGE
        ping_rate_hz = 1 / ping_rate

        # area
        area = float(max_length * min_length)

        # footpring calculation
        half_beam_width_radians = np.radians(beam_width / 2)
        sonar_footprint = 2 * average_depth * np.tan(half_beam_width_radians)

        # surveying velocity calculation
        velocity_m_s = sonar_footprint * ping_rate_hz    # CHANGE
        velocity_knots = velocity_m_s * 1.944

        # Adjusting max speed for best survey
        if velocity_knots > 8:
            velocity_knots = 8
            velocity_m_s = 8 / 1.944

        # re-calculating ping rate and velocity with the previous adjust, considering 100% ensonification along track
        ping_rate_hz = velocity_m_s / sonar_footprint
        if ping_rate_hz > 20:
            ping_rate_hz = 20
            velocity_m_s = sonar_footprint * ping_rate_hz
            velocity_knots = velocity_m_s * 1.944

        # calculating line spacing and total survey time
        reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines = \
            f.line_spacing(area, max_length, min_length, selected_option, average_depth)

        survey_time_minutes = ((total_reg_lines * min_length + total_cross_lines * max_length) / velocity_m_s) / 60
        survey_time_rounded = round(survey_time_minutes)
        unit = 'minutos'

        if survey_time_rounded >= 60:
            survey_time_rounded = round(survey_time_rounded / 60)
            unit = 'horas'
        total_time = round(survey_time_rounded * 1.25)

        # results
        results = {
            'Área total do levantamento': f'{area:.2f} m²',
            'Ping Rate Máximo recomendado': f'{ping_rate_hz:.2f} Hertz',
            'Espaçamento das linhas regulares de sondagem': f'{reg_line_spacing:.2f} m',
            'Espaçamento das linhas de verificação': f'{cross_line_spacing:.2f} m',
            'Tempo estimado para levantamento das linhas': f'{survey_time_rounded:.1f} {unit}',
            'Tempo total estimado para o levantamento': f'{total_time:.1f} {unit}',
            'Velocidade de navegação recomendada para uma cobertura de 100%': f'{velocity_knots:.2f} nós'
        }

        pdf_file = f.generate_pdf_report(results, title="Relatório de Planejamento de Campanha Batimétrica"
                                       )
        return results, sonar_footprint, pdf_file

    except ValueError:
        st.error("Por favor, insira valores válidos.")
        return None, None, None


st.title("GBS - GPHIDRO BathyScape")
st.write("Planejamento de campanhas batimétricas")

col1, col2 = st.columns(2)
with col1:
    parameters = st.selectbox("Escolha como deseja inserir a área do levantamento:",
                              ["Manual", "Upload de arquivo SHP"])
    max_length = st.number_input("Comprimento máximo da área (m):", min_value=0.0, step=5.0,
                                 help='Comprimento da maior feição da área')
    min_length = st.number_input("Comprimento mínimo da área (m):", min_value=0.0, step=5.0,
                                 help='Comprimento da menor feição da área')
    average_depth = st.number_input("Profundidade média da área (m):", min_value=0.0, step=5.0,
                                    help='Profundidade média da área')
    sonar_range = st.number_input("Faixa de operação do sonar (m):", min_value=0.0, step=5.0,
                                  help='Faixa máxima de operação do sonar')
    sound_speed = st.number_input("Velocidade do som na água (m/s):", min_value=0.0, step=1.0,
                                  help='Velocidade do som na água')
    beam_width = st.number_input("Largura do feixe (graus):", min_value=0.0, step=1.0,
                                 help='Largura do feixe do sonar em graus')
    selected_option = st.selectbox("Escolha uma opção de espaçamento de linha:",
                                   ["Normam", "ANA-UHE", "ANA-PCH"])
    coverage_percentage = st.slider("Cobertura do levantamento (%)", min_value=0, max_value=200, value=100,
                                    help='Porcentagem de cobertura do levantamento')
    st.write("### Cobertura do levantamento ao longo da linha:", coverage_percentage, "%")
    f.draw_footprint(coverage_percentage)

with col2:
    if st.button("Calcular"):
        results, sonar_footprint, pdf_file = calculate(max_length, min_length, average_depth, sonar_range, sound_speed,
                                                       beam_width, selected_option)
        if results:
            st.write("### Resultados:")
            for key, value in results.items():
                st.write(f"{key}: {value}")
            st.download_button(label="Baixar Relatório em PDF", data=pdf_file, file_name="Relatório.pdf",
                               mime="application/pdf")

with st.sidebar:
    st.header("Menu")
    st.button("Ajuda")
    st.button("Sobre")
    if 'pdf_file' in locals():
        st.download_button(label="Baixar Relatório", data=pdf_file, file_name="Relatório.pdf", mime="application/pdf")

    file = st.file_uploader("Upload de arquivo SHP ", type=['zip', 'rar'])

    if file:
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                extracted_files = f.extract_files(file, temp_dir)
                shapefiles = [f for f in extracted_files if f.endswith('.shp')]

                if not shapefiles:
                    st.error("O arquivo comprimido não contém um shapefile (.shp).")
                else:
                    shapefile_path = shapefiles[0]
                    total_area = f.process_shapefile(shapefile_path)
                    st.write(f"Área total calculada: {total_area:.2f} metros quadrados")
                    with col2:
                        f.plot_shapefile(shapefile_path)
            except Exception as e:
                        st.error(f"Erro ao processar o arquivo: {e}")





