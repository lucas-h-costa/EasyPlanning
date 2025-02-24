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
    st.info("Easy Planning é uma aplicação web para planejamento de campanhas batimétricas. \n"
             "Desenvolvido por Lucas Costa (lucas.h.costa@ufv.br)  - Grupo de Pesquisa em Hidrografia - GPHIDRO. \n"
             "Para mais informações, acesse: [GPHIDRO](https://gphidro.com.br/).\n")
    
def download_report():
    st.write('relatorio')
    
    
st.title("Easy Planning ", )
st.write("Planejamento de campanhas batimétricas")

tab1, tab2, tab3 = st.tabs(["Planejamento de Linhas", "Tempo de levantamento", 'Sobreposição'])  

with tab1: 
    st.header("Planejamento de Linhas")                      
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_length = st.number_input("Comprimento máximo da área (m):", min_value=0.0, step=5.0,
                                    help='Comprimento da maior feição da área', key='max_length')
        min_length = st.number_input("Comprimento mínimo da área (m):", min_value=0.0, step=5.0,
                                    help='Comprimento da menor feição da área', key='min_length')
        average_depth = st.number_input("Profundidade média da área (m):", min_value=0.0, step=5.0,
                                        help='Profundidade média da área', key='average_depth')


    with col2:
        sonar_range = st.number_input("Alcance do sonar (m):", min_value=0.0, step=5.0,   #ttirar
                                   help='Alcance do sonar em metros', key='sonar-range') 
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
        
        if st.button("Planejar"):
            area = max_length * min_length
            reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines = f.line_spacing(area, max_length, min_length, selected_option, average_depth, reg_line_spacing, cross_line_spacing,
                  scale, generate_cross_lines)
            with col3:
                st.write(f"Espaçamento das linhas regulares de sondagem: {reg_line_spacing:.2f} m")
                st.write(f"Espaçamento das linhas de verificação: {cross_line_spacing:.2f} m")
                st.write(f"Total de linhas regulares de sondagem: {total_reg_lines}")
                st.write(f"Total de linhas de verificação: {total_cross_lines}")
            
with tab2:
    st.header("Tempo de levantamento")
    col1, col2, col3 = st.columns(3)
    with col1:
        nav_speed = st.number_input("Velocidade de navegação (nós):", min_value=0.0, step=1.0,
                                help='Velocidade de navegação em nós', key='nav_speed')
        sound_speed = st.number_input("Velocidade do som na água (m/s):", min_value=0.0, step=1.0, #tirar
                                    help='Velocidade do som na água', key='sound_speed')#
    with col2:
       
        frequency = st.number_input("Frequência do sonar (kHz):", min_value=0.0, step=5.0, #tirar
                                    help='Frequência do sonar em kHz', key='frequency')
                
        time_between_lines = st.number_input("Tempo entre linhas (min):", min_value=0.0, step=1.0,
                                        help='Tempo de translado entre linhas em minutos', key='time_between_lines')
        if st.button("Calcular"):
            time, unit = f.calculate_survey_time(reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines,min_length,
                          max_length, nav_speed, time_between_lines #contour_length
                          )
            with col3:   
                st.write(f"Tempo de levantamento calculado: {time:.2f} {unit}")
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
            sound_speed = st.number_input("Velocidade do som na água (m/s):", min_value=0.0, step=1.0, #tirar
                                    help='Velocidade do som na água', key='sound_speed1')#
            sonar_range = st.number_input("Alcance do sonar (m):", min_value=0.0, step=5.0,   #ttirar
                                   help='Alcance do sonar em metros', key='sonar-range1') 
    with col3:
            if st.button("gerar sobreposição"):
                ping_rate_hz = f.calculate_ping_rate(sonar_range, sound_speed, frequency)
                footprint = f.calculate_sonar_footprint(beam_width, sonar_range)
                f.draw_footprint(coverage_percentage)
                st.write(f"pegada de cobertura do sonar: {footprint:.2f} m²")
                overlap = f.calculate_overlap(footprint, sonar_range, nav_speed, ping_rate_hz)
                st.write(f"Sobreposição calculada: {overlap:.2f} m")
            
        
        
with st.sidebar:
        st.header("Menu")
        if st.button("Ajuda"):
            ajuda()
        if st.button("Sobre"):
            sobre()
        if st.button('Relatório'):
            download_report()
       

        file = st.file_uploader("Upload de arquivo KML", type=['kml'])
        axe = st.file_uploader("Upload do eixo do reservatório", type=['kml'])

        if file:
            if axe: 
                try: # Cálculo com eixo fornecido pelo usuário
                    with st.sidebar:   # Extrair arquivos do eixo e do poligono principal
                        gdf_axe = gpd.read_file(axe, driver = 'kml')
                        gdf_axe['geometry'] = gdf_axe['geometry'].simplify(5, preserve_topology=True)
                        gdf = gpd.read_file(file, driver = 'kml')
                
                                    # Verificar se o eixo e o poligono principal foram carregados corretamente
                        if gdf_axe.empty:
                            st.error("O kml do eixo está vazio ou não pôde ser carregado.")
                        elif gdf.empty:
                            st.error("O kml principal está vazio ou não pôde ser carregado.")
                        else:
                            
                                    # Calcular informações e áreas dos poligonos
                                max_length = gdf_axe.geometry.length.sum()
                                st.write(f"Comprimento total do eixo: {max_length}")
                                                
                                info = f.calculate_axes_lengths(file)
                                gdf_utm = f.ensure_utm_crs(gdf)
                                total_area = gdf_utm.geometry.area.sum()            
                                gdf_contour = gdf.copy()
                                gdf_contour['geometry'] = gdf_contour.buffer(-10)
                                contour_length = gdf_contour.boundary.length.sum()
                    
                                st.write(f"Área total calculada: {total_area:.2f} m²")
                                st.write(info)
                                                # Plotar os poligonos sobrepostos
                                f.plot_shapefile_with_shp_axes(file, axe)
                            
                    with tab1:   
                                col1, col2, col3 = st.columns(3)
                                with col2:
                                    if st.button("Planejar com arquivo kml"):
                                        reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines =  f.line_spacing(total_area, float(info.get('comprimento em x')), float(info.get('comprimento em y')), selected_option, average_depth, reg_line_spacing, cross_line_spacing,
                        scale, generate_cross_lines)
                                        with col3:
                                            st.write(f"Espaçamento das linhas regulares de sondagem: {reg_line_spacing:.2f} m")
                                            st.write(f"Espaçamento das linhas de verificação: {cross_line_spacing:.2f} m")
                                            st.write(f"Total de linhas regulares de sondagem: {total_reg_lines}")
                                            st.write(f"Total de linhas de verificação: {total_cross_lines}")
                                            
                                                
                                            temp_dir, file_paths = f.plot_shapefile_with_grids_shp(file, reg_line_spacing, cross_line_spacing, axe)

                                                    # Disponibiliza o download do shapefile como um arquivo zip
                                            if temp_dir and file_paths:
                                                f.download_shapefile_as_zip(temp_dir, file_paths)
                                            '''if pdf_file:
                                                    st.download_button(label="Baixar Relatório em PDF", key='pdf', data=pdf_file,
                                                            file_name="Relatório.pdf", mime="application/pdf")'''
                except Exception as e:
                    st.error(f"Erro ao processar o arquivo: {e}")
                                            
            else:     
                    try:    #calculating with axe from function  ####################################################################
                        with st.sidebar:
                                gdf = gpd.read_file(file)
                                gdf_utm = f.ensure_utm_crs(gdf)
                                total_area = gdf_utm.geometry.area.sum()
                                gdf_contour = gdf.copy()
                                gdf_contour['geometry'] = gdf_contour.buffer(-2)
                                contour_length = gdf_contour.boundary.length.sum()
                                st.write(f"Área total calculada: {total_area:.2f} m^2")
                                info = f.calculate_axes_lengths(file)
                                st.write(info)
                                f.plot_shapefile_with_axes(file)
                        with tab1:
                            col1, col2, col3 = st.columns(3)
                            with col2:
                                        if st.button("Planejar com arquivo kml"):     #calculate using shapefile props 
                                            reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines =  f.line_spacing(total_area, float(info.get('comprimento em x')), float(info.get('comprimento em y')), selected_option, average_depth, reg_line_spacing, cross_line_spacing,
                            scale, generate_cross_lines)
                                            with col3:
                                                st.write(f"Espaçamento das linhas regulares de sondagem: {reg_line_spacing:.2f} m")
                                                st.write(f"Espaçamento das linhas de verificação: {cross_line_spacing:.2f} m")
                                                st.write(f"Total de linhas regulares de sondagem: {total_reg_lines}")
                                                st.write(f"Total de linhas de verificação: {total_cross_lines}")
                                        
                                                '''st.download_button(label="Baixar Relatório em PDF", data=pdf_file, file_name="Relatório.pdf",
                                                                    mime="application/pdf")'''
                                                temp_dir, file_paths = f.plot_shapefile_with_grids(gdf, reg_line_spacing, cross_line_spacing)

                                                            # Disponibiliza o download do shapefile como um arquivo zip
                                                if temp_dir and file_paths:
                                                    f.download_shapefile_as_zip(temp_dir, file_paths)
                                                '''if pdf_file:
                                                    st.download_button(label="Baixar Relatório em PDF", key='pdf',data=pdf_file, file_name="Relatório.pdf",
                                                                    mime="application/pdf")'''
                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo: {e}")

