import numpy as np
import streamlit as st
import functions as f     ### arquivo auxiliar com as funções
import tempfile
import pandas as pd
import geopandas as gpd



st.set_page_config(page_title="Easy Planning", page_icon="pageIcon.jpg", layout="wide")


def ajuda():
    st.write("### Ajuda")
    st.info( 'Para calcular o planejamento de campanhas batimétricas, siga os seguintes passos: \n'
             '1. Insira os parâmetros de entrada no lado esquerdo da tela. \n'
             '2. Clique no botão "Calcular". \n'
             '3. Os resultados serão exibidos no lado direito da tela. \n')


def sobre():
    st.write("### Sobre")
    st.info("Easy Planning é uma aplicação web para planejamento de campanhas batimétricas. \n")
    st.info("Easy Planning é uma aplicação web para planejamento de campanhas batimétricas. \n"
             "Desenvolvido por Lucas Costa (lucas.h.costa@ufv.br)  - Grupo de Pesquisa em Hidrografia - GPHIDRO. \n"
             "Para mais informações, acesse: [GPHIDRO](https://gphidro.com.br/).\n")
    


def calculate(max_length, min_length,area, average_depth, sonar_range, sound_speed, beam_width, selected_option, generate_cross_lines, frequency,
              reg_line_spacing, cross_line_spacing, scale, contour_length ):
    try:

        # ping rate calculation
        ping_rate_hz = f.calculate_ping_rate(sonar_range, sound_speed, frequency)

        area = area

        # sonar footprint calculation
        sonar_footprint = f.calculate_sonar_footprint(beam_width, sonar_range)

        #navigation speed calculation
        velocity_m_s, velocity_knots = f.calculate_velocity(sonar_footprint, ping_rate_hz)

        reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines = f.line_spacing(
            area, max_length, min_length, selected_option, average_depth, reg_line_spacing, cross_line_spacing,
            scale, generate_cross_lines
        )

        # survey time calculation
        survey_time_rounded, total_time, unit = f.calculate_survey_time(
            reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines, min_length, max_length,
            nav_speed, contour_length
        )

        
        results = {
            'Área total do levantamento': f'{area:.2f} m²',
            'Ping Rate teórico máximo calculado': f'{ping_rate_hz:.2f} Hertz',
            'Espaçamento das linhas regulares de sondagem': f'{reg_line_spacing:.2f} m',
            'Espaçamento das linhas de verificação': f'{cross_line_spacing:.2f} m',
            'Tempo estimado para levantamento das linhas, com base na velocidade informada': f'{survey_time_rounded:.1f} {unit}',
            'Tempo total estimado para o levantamento, com base na velocidade informada': f'{total_time:.1f} {unit}',
            'Velocidade de navegação máxima para uma cobertura de 100%': f'{velocity_knots:.2f} nós'
        }

        # Generate PDF report
        pdf_file = f.generate_pdf_report(results, title="Relatório de Planejamento de Campanha Batimétrica")

        
        if pdf_file is None:
            raise ValueError("Erro ao gerar o relatório em PDF.")

        return results, sonar_footprint, pdf_file

    except Exception as e:
        st.error(f"Erro ao calcular: {e}")
        return None, None, None
    
st.title(" GPHidro Easy Planning ", )
st.write("Planejamento de campanhas batimétricas")


col1, col2, col3 = st.columns(3)
with col1:
    max_length = st.number_input("Comprimento máximo da área (m):", min_value=0.0, step=5.0,
                                 help='Comprimento da maior feição da área')
    min_length = st.number_input("Comprimento mínimo da área (m):", min_value=0.0, step=5.0,
                                 help='Comprimento da menor feição da área')
    average_depth = st.number_input("Profundidade média da área (m):", min_value=0.0, step=5.0,
                                    help='Profundidade média da área')
    nav_speed = st.number_input("Velocidade de navegação (nós):", min_value=0.0, step=1.0,
                                help='Velocidade de navegação em nós')
    coverage_percentage = st.slider("Cobertura do levantamento (%)", min_value=0, max_value=200, value=100,
                                    help='Porcentagem de cobertura do levantamento')
    st.write("### Cobertura do levantamento ao longo da linha:", coverage_percentage, "%")
    f.draw_footprint(coverage_percentage) # alterar 

with col2:
    sonar_range = st.number_input("Alcance do sonar (m):", min_value=0.0, step=5.0,
                                  help='Alcance do sonar em metros')
    sound_speed = st.number_input("Velocidade do som na água (m/s):", min_value=0.0, step=1.0,
                                  help='Velocidade do som na água')
    frequency = st.number_input("Frequência do sonar (kHz):", min_value=0.0, step=5.0,
                                help='Frequência do sonar em kHz')
    beam_width = st.number_input("Largura do feixe (graus):", min_value=0.0, step=1.0,
                                 help='Largura do feixe do sonar em graus')
    selected_option = st.selectbox("Escolha uma opção de espaçamento de linha:",
                                   ["Normam", "ANA-UHE", "ANA-PCH", "Escala", "Personalizado"])
    generate_cross_lines = st.checkbox("Gerar Linhas de Verificação")
    
    scale = 0
    if selected_option == "Personalizado":     
        reg_line_spacing = st.number_input("Espaçamento das linhas regulares de sondagem (m):", min_value=0.0, step=5.0,
                                           help='Espaçamento das linhas regulares de sondagem')
        if generate_cross_lines:
            cross_line_spacing = st.number_input("Espaçamento das linhas de verificação (m):", min_value=0.0, step=5.0,
                                           help='Espaçamento das linhas de verificação')
        else: cross_line_spacing = 0 
        
    elif selected_option == "Escala":
        scale = st.number_input("Escala(1/xxx):", min_value=0.0, step=1.0, help='Escala da carta')
        reg_line_spacing = 0.005 * scale 
        if generate_cross_lines:
            cross_line_spacing = reg_line_spacing * 10
        else: cross_line_spacing = 0

    else:
        reg_line_spacing = 0
        cross_line_spacing = 0
        scale = 0
    
    if st.button("Calcular"):
        area = max_length * min_length
        results, sonar_footprint, pdf_file = calculate(max_length, min_length, area, average_depth, sonar_range,
                                                       sound_speed, beam_width, selected_option, generate_cross_lines, frequency, reg_line_spacing ,
                                                         cross_line_spacing, scale, contour_length = 0)

        if results:
            with col3:
                st.write("### Resultados:")
                for key, value in results.items():
                    st.write(f"{key}: {value}")
                if pdf_file:
                    st.download_button(label="Baixar Relatório em PDF", data=pdf_file, file_name="Relatório.pdf",
                                    mime="application/pdf")

with st.sidebar:
    st.header("Menu")
    if st.button("Ajuda"):
        ajuda()
    if st.button("Sobre"):
        sobre()
    if 'pdf_file' in locals() and pdf_file:
        st.download_button(label="Baixar Relatório", data=pdf_file, file_name="Relatório.pdf", mime="application/pdf")

    file = st.file_uploader("Upload de arquivo SHP", type=['zip', 'rar'])
    axe = st.file_uploader("Upload do eixo do reservatório", type=['zip', 'rar'])

    if file:
        if axe:  # Cálculo com eixo fornecido pelo usuário
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Extrair arquivos do eixo e do shapefile principal
                    st.write("Extraindo arquivos do eixo...")
                    extracted_files_axe = f.extract_files(axe, temp_dir)
                    st.write("Extraindo arquivos do shapefile principal...")
                    extracted_files_shp = f.extract_files(file, temp_dir)

                    # Verificar e identificar arquivos .shp extraídos
                    shapefiles = [f for f in extracted_files_shp if f.endswith('.shp')]
                    axe_files = [f for f in extracted_files_axe if f.endswith('.shp')]

                    if not shapefiles: 
                        st.error("O arquivo principal não contém um shapefile (.shp).")
                    elif not axe_files: 
                        st.error("O arquivo comprimido do eixo não contém um shapefile (.shp).")
                    else:
                        shp_file_path = axe_files[0]
                        shapefile_path = shapefiles[0]

                        # Ler os shapefiles extraídos
                        st.write("Carregando o shapefile do eixo...")
                        gdf_axe = gpd.read_file(shp_file_path)
                        st.write("Carregando o shapefile principal...")
                        gdf = gpd.read_file(shapefile_path)
    
                        # Verificar se o eixo e o shapefile principal foram carregados corretamente
                        if gdf_axe.empty:
                            st.error("O shapefile do eixo está vazio ou não pôde ser carregado.")
                        elif gdf.empty:
                            st.error("O shapefile principal está vazio ou não pôde ser carregado.")
                        else:
                            with st.sidebar:
                            # Calcular informações e áreas dos shapefiles
                                max_length = gdf_axe.geometry.length.sum()
                                st.write(f"Comprimento total do eixo: {max_length}")
                                    
                                info = f.calculate_axes_lengths(shapefile_path)
                                
                                total_area = gdf.geometry.area.sum()
                                gdf_contour = gdf.copy()
                                gdf_contour['geometry'] = gdf_contour.buffer(-10)
                                contour_length = gdf_contour.boundary.length.sum()
        
                                st.write(f"Área total calculada: {total_area:.2f} m²")
        
                                    # Plotar os shapefiles sobrepostos
                                f.plot_shapefile_with_shp_axes(shapefile_path, shp_file_path)

                except Exception as e:
                    st.error(f"Erro ao processar os arquivos: {e}")


                    with col2:
                        if st.button("Calcular com arquivo SHP"):
                            results, sonar_footprint, pdf_file = calculate(max_length, float(info.get('comprimento em x')), total_area,
                                                                        average_depth, sonar_range, sound_speed,
                                                                        beam_width, selected_option, frequency,
                                                                        reg_line_spacing, cross_line_spacing, scale, contour_length)
                            if results:
                                reg_line_spacing = float(results.get('Espaçamento das linhas regulares de sondagem').split()[0])
                                cross_line_spacing = float(results.get('Espaçamento das linhas de verificação').split()[0])
                                st.write("### Resultados:")
                                for key, value in results.items():
                                    st.write(f"{key}: {value}")
                                st.download_button(label="Baixar Relatório em PDF", data=pdf_file, file_name="Relatório.pdf",
                                                mime="application/pdf")
                                temp_dir, file_paths = f.plot_shapefile_with_grids_shp(gdf, reg_line_spacing, cross_line_spacing, gdf_axe)

                                # Disponibiliza o download do shapefile como um arquivo zip
                                if temp_dir and file_paths:
                                    f.download_shapefile_as_zip(temp_dir, file_paths)
                                if pdf_file:
                                    st.download_button(label="Baixar Relatório em PDF", key='pdf', data=pdf_file,
                                                    file_name="Relatório.pdf", mime="application/pdf")
                            
        else:     
            with tempfile.TemporaryDirectory() as temp_dir:
                try:    #calculating with axe from function  ####################################################################
                    extracted_files = f.extract_files(file, temp_dir)
                    shapefiles = [f for f in extracted_files if f.endswith('.shp')]

                    if not shapefiles:
                        st.error("O arquivo comprimido não contém um shapefile (.shp).")
                    else:
                        shapefile_path = shapefiles[0]
                        gdf = gpd.read_file(shapefile_path)
                        total_area = gdf.geometry.area.sum()
                        gdf_contour = gdf.copy()
                        gdf_contour['geometry'] = gdf_contour.buffer(-10)
                        contour_length = gdf_contour.boundary.length.sum()
                        st.write(f"Área total calculada: {total_area:.2f} m^2")
                        info = f.calculate_axes_lengths(shapefile_path)
                        st.write(info)
                        f.plot_shapefile_with_axes(shapefile_path)
                        with col2:
                            if st.button("Calcular com arquivo SHP"):     #calculate using shapefile props 
                                results, sonar_footprint, pdf_file = calculate(float(info.get('comprimento em y')),
                                                                            float(info.get('comprimento em x')), total_area,
                                                                            average_depth, sonar_range, sound_speed,
                                                                            beam_width, selected_option, frequency,
                                                                            reg_line_spacing, cross_line_spacing, scale, contour_length)
                                if results:
                                    reg_line_spacing = float(results.get('Espaçamento das linhas regulares de sondagem').split()[0])
                                    cross_line_spacing = float(results.get('Espaçamento das linhas de verificação').split()[0])
                                    st.write("### Resultados:")
                                    for key, value in results.items():
                                        st.write(f"{key}: {value}")
                                    st.download_button(label="Baixar Relatório em PDF", data=pdf_file, file_name="Relatório.pdf",
                                                    mime="application/pdf")
                                    temp_dir, file_paths = f.plot_shapefile_with_grids(gdf, reg_line_spacing, cross_line_spacing)

                                            # Disponibiliza o download do shapefile como um arquivo zip
                                if temp_dir and file_paths:
                                    f.download_shapefile_as_zip(temp_dir, file_paths)
                                if pdf_file:
                                    st.download_button(label="Baixar Relatório em PDF", key='pdf',data=pdf_file, file_name="Relatório.pdf",
                                                    mime="application/pdf")
                except Exception as e:
                    st.error(f"Erro ao processar o arquivo: {e}")

