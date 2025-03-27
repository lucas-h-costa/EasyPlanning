import numpy as np
import streamlit as st
import functions as f     ### arquivo auxiliar com as funções
import tempfile
import geopandas as gpd
from shapely.geometry import Polygon, LineString


st.set_page_config(page_title="Easy Planning", page_icon="pageIcon.jpg", layout="wide")


def ajuda():
    st.write("### Ajuda")
    st.info( 'Para calcular o planejamento de campanhas batimétricas, siga os seguintes passos: \n'
             '1. Insira os parâmetros de entrada no lado esquerdo da tela. \n'
             '2. Clique no botão "Planejar". \n'
             '3. Os resultados serão exibidos no lado direito da tela. \n')


def sobre():
    st.write("### Sobre") 
    st.info("Easy Planning é uma aplicação web para planejamento de campanhas batimétricas. \n"
             "Desenvolvido por Lucas Costa (lucas.h.costa@ufv.br)  - Grupo de Pesquisa em Hidrografia - GPHIDRO. \n"
             "Para mais informações, acesse: [GPHIDRO](https://gphidro.com.br/).\n")
    
def download_report():
    st.write('relatorio')
    
    
st.title("Easy Planner" )
st.write("Planejamento de campanhas batimétricas")
st.write("Versão 0.1")

tab1, tab2, tab3 = st.tabs(["Planejamento de Linhas", "Tempo de levantamento", 'Sobreposição'])  

with tab1: 
    st.header("Planejamento de Linhas")                      
    col1, col2, col3 = st.columns(3)
    
    with col1:
        average_depth = st.number_input("Profundidade média da área (m):", min_value=0.0, step=5.0,
                                        help='Profundidade média da área', key='average_depth')
        crs= st.text_input("Sistema de referência de coordenadas (CRS) da área:", "EPSG:31983",
                            help='Sistema de referência de coordenadas da área', key='crs')


    with col2:
        #sonar_range = st.number_input("Alcance do sonar (m):", min_value=0.0, step=5.0,   #ttirar
                                  # help='Alcance do sonar em metros', key='sonar-range') 
        selected_option = st.selectbox("Escolha uma opção de espaçamento de linha:",
                                    ["Normam", "ANA-UHE", "ANA-PCH", "Escala", "Personalizado"])
        scale = 0  # Inicializando `scale` como padrão
        generate_cross_lines = st.checkbox("Gerar Linhas de Verificação")  # Já está sendo definida

        if generate_cross_lines:
            cross_line_spacing = st.selectbox("Escolha o fator de multiplicação para o espaçamento das LVs:", [1, 2, 3, 4, 5, 10, "personalizado"])
            if cross_line_spacing == "personalizado":
             cross_line_spacing = st.number_input("Fator de multiplicação para o espaçamento das LVs:", min_value=0, step=1, help='Fator de multiplicação para o espaçamento das LVs')
        
        if selected_option == "Personalizado":     
            reg_line_spacing = st.number_input("Espaçamento das linhas regulares de sondagem (m):", min_value=0.0, step=5.0, help='Espaçamento das linhas regulares de sondagem')
            if generate_cross_lines:
                cross_line_spacing = st.number_input("Espaçamento das linhas de verificação (m):", min_value=0.0, step=5.0, help='Espaçamento das linhas de verificação')
            else:
                cross_line_spacing = 0 

        elif selected_option == "Escala":
            scale = st.number_input("Escala(1/xxx):", min_value=0.0, step=1.0, help='Escala da carta')
            reg_line_spacing = 0.005 * scale 
            if generate_cross_lines:
                cross_line_spacing = reg_line_spacing * 10
            else:
                cross_line_spacing = 0

        else:
            reg_line_spacing = reg_line_spacing = 0
            cross_line_spacing = cross_line_spacing
            scale = 1 # Definindo um valor padrão para `scale` no caso de outras opções

                  
with st.sidebar:
        st.header("Menu")
        if st.button("Ajuda"):
            ajuda()
        if st.button("Sobre"):
            sobre()

       

        file = st.file_uploader("Upload de arquivo KML", type=['kml'])
        axe = st.file_uploader("Upload do eixo do reservatório", type=['kml'])

        if file:
            if axe: 
                try: # Cálculo com eixo fornecido pelo usuário
                    with st.sidebar:   # Extrair arquivos do eixo e do poligono principal
                        gdf_axe = gpd.read_file(axe, driver = 'kml')
                        gdf_axe['geometry'] = gdf_axe['geometry'].simplify(5, preserve_topology=True)
                        gdf_axe = gdf_axe.to_crs(crs)
                        gdf = gpd.read_file(file, driver = 'kml')
                        gdf = gdf.to_crs(crs)
                
                                    # Verificar se o eixo e o poligono principal foram carregados corretamente
                        if gdf_axe.empty:
                            st.error("O arquivo do eixo está vazio ou não pôde ser carregado.")
                        elif gdf.empty:
                            st.error("O arquivo principal está vazio ou não pôde ser carregado.")
                        else:
                            
                                    # Calcular informações e áreas dos poligonos
                                max_length = gdf_axe.geometry.length.sum()
                                st.write(f"Comprimento total do eixo: {max_length:.2f} m")
                                polygon = gdf.geometry.iloc[0]  

                                # Obtenha o retângulo rotacionado mínimo do polígono
                                min_rotated_rect = polygon.minimum_rotated_rectangle

                                # Obtenha os vértices do retângulo (deve ser um objeto Polygon com 5 pontos, o último repete o primeiro)
                                rect_coords = list(min_rotated_rect.exterior.coords)

                                # Calcule os comprimentos dos lados do retângulo
                                side1 = LineString([rect_coords[0], rect_coords[1]]).length
                                side2 = LineString([rect_coords[1], rect_coords[2]]).length

                                # O menor eixo será o menor entre os dois lados
                                min_length = min(side1, side2)             
                                total_area = gdf.geometry.area.sum() 
                                area_ha = total_area/10000           
                                gdf_contour = gdf.copy()
                                gdf_contour['geometry'] = gdf_contour.buffer(-10)
                                contour_length = gdf_contour.boundary.length.sum()
                                st.session_state.contour_length = contour_length
                                st.write(gdf.geometry)
                                st.write(gdf_axe.geometry)
                                st.write(f'Comprimento do eixo: {max_length:.2f} m')
                                st.write(f'Comprimento do menor lado do retângulo rotacionado: {min_length:.2f} m')
                                st.write(f"Área total calculada: {total_area:.2f} m²")
                                st.write(f"Área total calculada em hectares: {total_area/10000:.2f} ha")
                                st.write(f"Comprimento total do contorno: {contour_length:.2f} m")
                                                # Plotar os poligonos sobrepostos
                                f.plot_area_with_axes(file, axe, crs)
                            
                    with tab1:   
                                col1, col2, col3 = st.columns(3)
                                with col2:
                                    if st.button("Planejar"):
                                        reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines =  f.line_spacing(total_area, area_ha,  max_length, min_length, selected_option, average_depth, reg_line_spacing, cross_line_spacing,
                  scale, generate_cross_lines)
                                        st.session_state.reg_line_spacing = reg_line_spacing
                                        st.session_state.cross_line_spacing = cross_line_spacing
                                        st.session_state.total_reg_lines = total_reg_lines
                                        st.session_state.total_cross_lines = total_cross_lines
                                        st.session_state.min_length = min_length
                                        st.session_state.max_length = max_length
                                        with col3:
                                            st.write(f"Espaçamento das linhas regulares de sondagem: {reg_line_spacing:.2f} m")
                                            st.write(f"Espaçamento das linhas de verificação: {cross_line_spacing:.2f} m")
                                            st.write(f"Total de linhas regulares de sondagem: {total_reg_lines}")
                                            st.write(f"Total de linhas de verificação: {total_cross_lines}")
                                            
                                                
                                            temp_dir, file_paths = f.plot_area_with_grids(file, reg_line_spacing, cross_line_spacing, axe, crs)

                                                    # Disponibiliza o download  como um arquivo zip
                                            if temp_dir and file_paths:
                                                f.download_files_as_zip(temp_dir, file_paths)
                                            '''if pdf_file:
                                                    st.download_button(label="Baixar Relatório em PDF", key='pdf', data=pdf_file,
                                                            file_name="Relatório.pdf", mime="application/pdf")'''
                except Exception as e:
                    st.error(f"Erro ao processar o arquivo: {e}")
                                            
            else:     
                    st.error("Por favor, faça o upload do arquivo do eixo da área de interesse.")
        else:
            st.error("Por favor, faça o upload do arquivo KML da área de interesse.")
            
with tab2:
    st.header("Tempo de levantamento")
    col1, col2, col3 = st.columns(3)
    with col1:
        nav_speed = st.number_input("Velocidade de navegação (nós):", min_value=0.0, step=1.0,
                                help='Velocidade de navegação em nós', key='nav_speed')
        sound_speed = st.number_input("Velocidade do som na água (m/s):", min_value=0.0, step=1.0, #tirar
                                    help='Velocidade do som na água', key='sound_speed')#
    with col2:
                
        time_between_lines = st.number_input("Tempo entre linhas (min):", min_value=0.0, step=1.0,
                                        help='Tempo de translado entre linhas em minutos', key='time_between_lines')
        if st.button("Calcular"):
            time, unit = f.calculate_survey_time( nav_speed, time_between_lines, st.session_state.total_reg_lines, st.session_state.total_cross_lines,st.session_state.min_length,
                          st.session_state.max_length,st.session_state.contour_length)
            with col3:   
                st.write(f"Tempo de levantamento calculado: {time:.2f} {unit}")    
           
            st.session_state.stime = time
            st.session_state.unit = unit
            st.session_state.sound_speed = sound_speed
            

with tab3: 
   
    st.header('Cálculo de sobreposição') ################################# testar 
    col1, col2, col3 = st.columns(3)
    with col1:
            coverage_percentage = st.number_input("Porcentagem de cobertura (%):", min_value=0.0, max_value=100.0, step=1.0,
                                            help='Porcentagem de cobertura da área', key='coverage_percentage')
            beam_width = st.number_input("Largura do feixe do sonar (°):", min_value=0.0, step=1.0, 
                                    help='Largura do feixe do sonar em graus', key='beam_width')
            nav_speed = st.number_input("Velocidade de navegação (nós):", min_value=0.0, step=1.0,
                                help='Velocidade de navegação em nós', key='nav_speed1')
    with col2:
            frequency = st.number_input("Frequência do sonar (kHz):", min_value=0.0, step=1.0,
                                    help='Frequência do sonar em kHz', key='frequency')
            sound_speed = st.number_input("Velocidade do som na água (m/s):", min_value=0.0, step=1.0, #tirar
                                    help='Velocidade do som na água', key='sound_speed1')#
            sonar_range = st.number_input("Alcance do sonar (m):", min_value=0.0, step=5.0,   #ttirar
                                   help='Alcance do sonar em metros', key='sonar-range1') 
    with col3:
            if st.button("gerar sobreposição"):
                ping_rate_hz = f.calculate_ping_rate(sonar_range,sound_speed, frequency)
                footprint = f.calculate_sonar_footprint(beam_width, sonar_range)
                f.draw_footprint(coverage_percentage)
                st.write(f"pegada do sonar: {footprint:.2f} m²")
                overlap = f.calculate_overlap(footprint, sonar_range, nav_speed, ping_rate_hz)
                st.write(f"Sobreposição calculada: {overlap:.2f} %")
                st.write(f"Ping rate teórico máximo calculado: {ping_rate_hz:.2f} Hz")
                st.session_state.ping_rate_hz = ping_rate_hz
                st.session_state.footprint = footprint
                st.session_state.overlap = overlap
                st.session_state.coverage_percentage = coverage_percentage
                st.session_state.beam_width = beam_width
                st.session_state.frequency = frequency
                st.session_state.sonar_range = sonar_range
                st.session_state.nav_speed = nav_speed
    
    st.session_state.results = {"Espaçamento das linhas regulares":st.session_state.reg_line_spacing, "Espaçamento das linhas de verificação": st.session_state.cross_line_spacing,
               "Quantidade total de linhas regulares":st.session_state.total_reg_lines, "Quantidade total de linhas de verificação": st.session_state.total_cross_lines,
               "Perímetro da área":st.session_state.contour_length, "Tempo de levantamento":st.session_state.time, "Unidade de tempo":st.session_state.unit,
               "Velocidade de navegação":st.session_state.nav_speed, "Tempo de translado entre as linhas (em minutos)":st.session_state.time_between_lines,
               "Velocidade do som na água":st.session_state.sound_speed, "Ping rate teórico máximo": st.session_state.ping_rate_hz,
               "Pegada do sonar": st.session_state.footprint, "Sobreposição calculada": st.session_state.overlap, "Porcentagem de cobertura": st.session_state.coverage_percentage,
               "Largura do feixe do sonar": st.session_state.beam_width, "Frequência do sonar": st.session_state.frequency, "Alcance do sonar": st.session_state.sonar_range}   
        
                
                
with st.sidebar:
 new_report = st.button("Gerar Relatório")
 if new_report:
     f.generate_pdf_report(st.session_state.results)
     st.download_button(label="Baixar Relatório em PDF", key='pdf', data='report.pdf',
                            file_name="Relatório.pdf", mime="application/pdf")
