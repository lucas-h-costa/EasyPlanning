import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import streamlit as st
import geopandas as gpd
import pandas as pd
import zipfile
import rarfile
import tempfile
import os
import pyproj
import shapely.geometry as geom
from shapely.geometry import LineString, Point, Polygon, MultiPolygon
from shapely.ops import unary_union
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Image
from io import BytesIO
from datetime import datetime
from pyproj import CRS
import shutil

def calculate_ping_rate(sonar_range, sound_speed, frequency):
    """Calcula a taxa de ping a partir do alcance do sonar e da velocidade do som."""
    frequency_hz = frequency * 1000
    ping_rate = ((2*sonar_range) / sound_speed) + 2 * (10/frequency_hz)
    ping_rate_hz = 1 / ping_rate
    return ping_rate_hz

def calculate_sonar_footprint(beam_width, sonar_range):
    """Calcula a pegada do sonar com base na largura do feixe e na profundidade média."""
    half_beam_width_radians = np.radians(beam_width / 2)
    return 2 * sonar_range * np.tan(half_beam_width_radians)

def calculate_velocity(sonar_footprint, ping_rate_hz):
    """Calcula a velocidade de navegação com base na pegada do sonar e na taxa de ping."""
    velocity_m_s = sonar_footprint * ping_rate_hz
    velocity_knots = velocity_m_s * 1.944
    return velocity_m_s, velocity_knots

def calculate_overlap(footprint, sonar_range, nav_speed, ping_rate):
    overlap_percentage  = (footprint * ping_rate) / (nav_speed * 2)/100
    return overlap_percentage
def calculate_survey_time(reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines,min_length,
                          max_length, nav_speed, contour_length, time_between_lines):
    """Calcula o tempo estimado para o levantamento das linhas."""

    nav_speed_ms = nav_speed / 1.944
    survey_time_minutes = ((total_reg_lines * min_length + total_cross_lines * max_length + contour_length) / nav_speed_ms) / 60
    survey_time_rounded = round(survey_time_minutes)
    total_transladed_time = round((total_cross_lines+total_reg_lines) * time_between_lines)

    if survey_time_rounded >= 60:
        survey_time_rounded = round(survey_time_rounded / 60)
        
        unit = 'horas'
    else:
        unit = 'minutos'

    total_time = round(survey_time_rounded + total_transladed_time)

    return total_time, unit

def line_spacing(area, max_length, min_length, selected_option, average_depth, reg_line_spacing, cross_line_spacing,
                  scale, generate_cross_lines):
    km = max_length / 1000
    hectares = area / 10000

    if selected_option == 'Normam':

        reg_line_spacing = max(3 * average_depth, 25)
        if generate_cross_lines:
            cross_line_spacing = 10 * reg_line_spacing
        else: cross_line_spacing = 0
        
    elif selected_option == 'ANA-UHE':

        rls_km = (0.35 * (hectares ** 0.35)) / km
        reg_line_spacing = rls_km * 1000
        if generate_cross_lines: 
            cross_line_spacing = 3 * reg_line_spacing
        else: cross_line_spacing = 0

    elif selected_option == 'ANA-PCH':

        rls_km = (0.1 * (hectares ** 0.25)) / km
        reg_line_spacing = rls_km * 1000
        if generate_cross_lines:
            cross_line_spacing = 3 * reg_line_spacing
        else: cross_line_spacing = 0

    elif selected_option == 'Personalizado':

        reg_line_spacing = reg_line_spacing
        cross_line_spacing = cross_line_spacing

    elif selected_option == "Escala":

        reg_line_spacing = reg_line_spacing
        cross_line_spacing = cross_line_spacing

    if cross_line_spacing >= min_length/2:
        cross_line_spacing = min_length / 3

    total_reg_lines = round(max_length / reg_line_spacing)
    if generate_cross_lines:
        total_cross_lines = round(min_length / cross_line_spacing)
    else:
        total_cross_lines = 0

    return reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines

def draw_footprint(coverage_percentage):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    diameter = 10
    spacing = diameter * (1 - coverage_percentage / 100)  # Calcula o espaçamento com base na porcentagem de cobertura

    for i in range(5):
        circle = plt.Circle((10 + i * (diameter + spacing), 90), diameter / 2, edgecolor='red', facecolor='none',
                            lw=1)
        ax.add_patch(circle)

    ax.set_xlim(0, 50 + 5 * (diameter + spacing))
    ax.set_ylim(0, 100)
    ax.set_aspect('equal', 'box')
    ax.axis('off')

    st.pyplot(fig)

def generate_pdf_report(results, title="Relatório de Resultados"):  # generating report with the previous results
    logo_path = 'icon.png'
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    logo = Image(logo_path, width=0.5 * inch, height=0.5 * inch)  # Ajuste o tamanho conforme necessário
    logo.hAlign = 'LEFT'
    logo.vAlign = 'TOP'
    elements.append(logo)
    now = datetime.now()
    date = now.strftime("%d/%m/%Y")
    time = now.strftime("%H:%M:%S")

    # title style
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontSize = 24
    title_style.alignment = 1
    title_style.spaceAfter = 50

    # adding title
    elements.append(Paragraph(title, title_style))

    # adding date and time
    if date and time:
        date_time_style = styles['Normal']
        date_time_style.fontSize = 8
        date_time_paragraph = Paragraph(f"Data: {date}<br/>Hora: {time}", date_time_style)
        elements.append(date_time_paragraph)

    # adding results in table format
    table_data = [["Parâmetro", "Valor"]]  # table head
    for key, value in results.items():
        table_data.append([key, value])

    # table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # creating table
    table = Table(table_data)
    table.setStyle(table_style)
    elements.append(table)

    # build the PDF
    doc.build(elements)

    # returning pdf file in bytes, to be used in the download button (streamlit can not deal with pdf files directly)
    return buffer.getvalue()


def plot_area_with_axes(file, axe, crs):
    # Carregar os shapefiles
    try:
        gdf = gpd.read_file(file)
        gdf_axe = gpd.read_file(axe)
    except Exception as e:
        st.error(f"Erro ao carregar os arquivos shapefile: {e}")
        return

    # Verificar se o shapefile principal é um polígono
    if not all(gdf.geometry.type == 'Polygon'):
        st.error("O arquivo principal deve conter geometrias do tipo polígono.")
        return

    # Verificar se o arquivo de eixos é uma linha
    if not all(gdf_axe.geometry.type == 'LineString'):
        st.error("O arquivo de eixos deve conter geometrias do tipo linha.")
        return

    # Garantir que ambos os shapefiles estejam em CRS UTM
    gdf = gdf.to_crs(crs)
    gdf_axe = gdf_axe.to_crs(crs)

    # Criar figura e eixos
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plotar o shapefile principal (polígono)
    gdf.plot(ax=ax, color='lightblue', edgecolor='black', label='Área do levantamento')

    # Plotar o arquivo de eixos (linha)
    gdf_axe.plot(ax=ax, color='red', linewidth=2, label='Eixo principal')

    # Plotar contorno do polígono
    gdf.boundary.plot(ax=ax, color='purple', linewidth=1, label='Contorno da área')

    # Definir título e rótulos dos eixos
    plt.title('Visualização do Arquivo com o Eixo')
    plt.xlabel('Coordenada UTM (Eixo X)')
    plt.ylabel('Coordenada UTM (Eixo Y)')
    
    # Manter proporção correta no gráfico
    ax.set_aspect('equal')

    # Mostrar legenda
    plt.legend()

    # Remover grid
    plt.grid(False)

    # Exibir o gráfico no Streamlit
    st.pyplot(fig)


################ funcao para plotar tudo 
def plot_area_with_grids(file, reg_line_spacing, cross_line_spacing, axe, crs):
    """Função para gerar e plotar linhas de grid dentro do polígono de um reservatório."""
    gdf = gpd.read_file(file)
    gdf = gdf.to_crs(crs)
    axe_gdf = gpd.read_file(axe)
    axe_gdf = axe_gdf.to_crs(crs)
    
    '''if not all(gdf.geometry.type == 'Polygon'):
        st.error("O arquivo principal deve conter geometrias do tipo polígono.")
        return

    # Verificar se o arquivo de eixos é uma linha
    if not all(axe_gdf.geometry.type == 'LineString'):
        st.error("O arquivo de eixos deve conter geometrias do tipo linha.")
        return'''

    # Criar a linha de contorno com um buffer de 5 metros para dentro
    gdf_contour = gdf.copy()
    gdf_contour['geometry'] = gdf_contour.buffer(-5).buffer(0)  # Corrigir possíveis geometrias inválidas

    # Obter os limites do shapefile (bounding box)
    bounds = gdf_contour.total_bounds  # [minx, miny, maxx, maxy]

    # Criar listas para armazenar as linhas
    grid_lines_parallel = []  # Linhas paralelas (verificação)
    grid_lines_perpendicular = []  # Linhas perpendiculares (regulares)

    # **Gerar as linhas de verificação (paralelas ao eixo)**
    if axe_gdf is not None and not axe_gdf.empty:
        for line in axe_gdf.geometry:
            current_offset = 0
            while current_offset <= bounds[2] - bounds[0]:
                try:
                    # Gerar linha paralela à esquerda
                    offset_line_left = line.parallel_offset(current_offset, side='left')  # Linha paralela ao eixo, lado esquerdo
                    grid_lines_parallel.append(offset_line_left)

                    # Gerar linha paralela à direita
                    offset_line_right = line.parallel_offset(current_offset, side='right')  # Linha paralela ao eixo, lado direito
                    grid_lines_parallel.append(offset_line_right)
                    
                    current_offset += cross_line_spacing
                except Exception as e:
                    print(f"Erro ao gerar linha paralela com offset {current_offset}: {e}")
                    continue  # Se houver erro, continuar com o próximo valor de offset

    # **Gerar as linhas regulares (perpendiculares ao eixo) ao longo de toda a extensão**

    for line in gdf.geometry:
        # Gerar pontos e segmentos
        num_points = int(line.length // reg_line_spacing) + 1
        points = [line.interpolate(i * reg_line_spacing) for i in range(num_points)]

        for i in range(len(points) - 1):
            segment = LineString([points[i], points[i + 1]])
            mid = segment.interpolate(0.5, normalized=True)  # Ponto médio

            # Rotacionar 90° em torno do ponto médio
            coords = [(p.x - mid.x, p.y - mid.y) for p in segment.coords]
            rotated_coords = [(y, -x) for x, y in coords]  # Rotação de 90° (troca x ↔ y e inverte um eixo)
            rotated_segment = LineString([(x + mid.x, y + mid.y) for x, y in rotated_coords])

            # Estender a linha
            x1, y1 = rotated_segment.coords[-2]
            x2, y2 = rotated_segment.coords[-1]
            dx, dy = x2 - x1, y2 - y1  # Vetor direção do segmento
            length = np.sqrt(dx**2 + dy**2)
            unit_dx, unit_dy = dx / length, dy / length  # Normalizar o vetor direção

            # Calcular o ponto de extensão
            new_x = x2 + unit_dx * 1000
            new_y = y2 + unit_dy * 1000

            # Criar a linha estendida
            extended_segment = LineString([*rotated_segment.coords, (new_x, new_y)])

            grid_lines_perpendicular.append(extended_segment)
            

    # **Verificação e plotagem**
    if not grid_lines_perpendicular:
        print("Nenhuma linha perpendicular (regular) foi gerada.")
    else:
        print(f"{len(grid_lines_perpendicular)} linhas perpendiculares (regulares) foram geradas com sucesso!")

    # Criar GeoDataFrames para as linhas de grid
    gdf_grid_lines_parallel = gpd.GeoDataFrame(geometry=grid_lines_parallel, crs=gdf.crs)
    gdf_grid_lines_perpendicular = gpd.GeoDataFrame(geometry=grid_lines_perpendicular, crs=gdf.crs)

    # Realizar a interseção para garantir que as linhas fiquem dentro do contorno
    gdf_grid_lines_parallel = gpd.overlay(gdf_grid_lines_parallel, gdf_contour, how='intersection')
    gdf_grid_lines_perpendicular = gpd.overlay(gdf_grid_lines_perpendicular, gdf_contour, how='intersection')

    # Salvar os shapefiles modificados em um diretório temporário
    temp_dir = tempfile.mkdtemp()
    try:
        # Shapefile das linhas paralelas
        parallel_shapefile_path = os.path.join(temp_dir, "shapefile_linhas_paralelas.shp")
        gdf_grid_lines_parallel.to_file(parallel_shapefile_path)

        # Shapefile das linhas perpendiculares
        perpendicular_shapefile_path = os.path.join(temp_dir, "shapefile_linhas_perpendiculares.shp")
        gdf_grid_lines_perpendicular.to_file(perpendicular_shapefile_path)

        # Exibir o gráfico
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax, color='lightblue', edgecolor='black')  # Polígono do reservatório
        gdf_grid_lines_parallel.plot(ax=ax, color='red', linestyle='-', label='Linhas Paralelas')  # Linhas paralelas
        gdf_grid_lines_perpendicular.plot(ax=ax, color='green', linestyle='--', label='Linhas Perpendiculares')  # Linhas perpendiculares
        ax.set_title("Linhas de Grid Geradas")
        ax.legend()
        plt.show()

    except Exception as e:
        print(f"Erro ao salvar ou exibir as linhas: {e}")

def create_zip_from_directory(directory_path, zip_name):
    """Cria um arquivo zip a partir de um diretório."""
    zip_path = shutil.make_archive(zip_name, 'zip', directory_path)
    return zip_path

def download_files_as_zip(temp_dir, file_paths):
    """Disponibiliza o shapefile processado como um arquivo ZIP para download."""
    zip_name = "shapefiles"
    zip_path = create_zip_from_directory(temp_dir, zip_name)
    with open(zip_path, "rb") as f:
        st.download_button(label="Baixar Linhas Planejadas", data=f.read(), file_name=f"{zip_name}.zip", mime="application/zip")

    # Não remover o diretório temporário até que o download seja concluído
    return