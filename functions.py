import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import streamlit as st
import geopandas as gpd
import pandas as pd
import zipfile
import tempfile
import os
import pyproj
import shapely.geometry as geom
from shapely.geometry import LineString
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Image
from io import BytesIO
from datetime import datetime
import shutil


def set_default_values(beam_width, sound_speed, average_depth, max_length, min_length, sonar_range):
    """Define valores padrão se não forem fornecidos."""
    if beam_width is None:
        beam_width = 8
    if sound_speed is None:
        sound_speed = 1500
    if average_depth is None:
        average_depth = 35
    if max_length is None:
        max_length = 1000
    if min_length is None:
        min_length = 100
    if sonar_range is None:
        sonar_range = 35
    return beam_width, sound_speed, average_depth, max_length, min_length, sonar_range


def calculate_ping_rate(sonar_range, sound_speed, frequency):
    """Calcula a taxa de ping a partir do alcance do sonar e da velocidade do som."""
    frequency_hz = frequency * 1000
    double_range = 2 * sonar_range
    ping_rate = (double_range / sound_speed) + 2 * (10/frequency_hz)
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


def calculate_survey_time(reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines,min_length,max_length, nav_speed, contour_length):
    """Calcula o tempo estimado para o levantamento das linhas."""

    nav_speed_ms = nav_speed / 1.944
    survey_time_minutes = ((total_reg_lines * min_length + total_cross_lines * max_length + contour_length) / nav_speed_ms) / 60
    survey_time_rounded = round(survey_time_minutes)

    if survey_time_rounded >= 60:
        survey_time_rounded = round(survey_time_rounded / 60)
        unit = 'horas'
    else:
        unit = 'minutos'

    total_time = round(survey_time_rounded * 1.25)

    return survey_time_rounded, total_time, unit


def line_spacing(area, max_length, min_length, selected_option, average_depth, reg_line_spacing, cross_line_spacing,
                  scale):
    km = max_length / 1000
    hectares = area / 10000

    if selected_option == 'Normam':

        reg_line_spacing = max(3 * average_depth, 25)
        cross_line_spacing = 10 * reg_line_spacing

    elif selected_option == 'ANA-UHE':

        rls_km = (0.35 * (hectares ** 0.35)) / km
        reg_line_spacing = rls_km * 1000
        cross_line_spacing = 3 * reg_line_spacing

    elif selected_option == 'ANA-PCH':

        rls_km = (0.1 * (hectares ** 0.25)) / km
        reg_line_spacing = rls_km * 1000
        cross_line_spacing = 3 * reg_line_spacing

    elif selected_option == 'Personalizado':

        reg_line_spacing = reg_line_spacing
        cross_line_spacing = cross_line_spacing

    elif selected_option == "Escala":

        reg_line_spacing = reg_line_spacing
        cross_line_spacing = cross_line_spacing

    if cross_line_spacing >= min_length/2:
        cross_line_spacing = min_length / 3

    total_reg_lines = round(max_length / reg_line_spacing)
    total_cross_lines = round(min_length / cross_line_spacing)

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


def ensure_utm_crs(gdf):
    """Converte o CRS do GeoDataFrame para UTM, se necessário."""
    if gdf.crs.is_projected:
        return gdf

    # Obtém o CRS EPSG da geometria central do GeoDataFrame
    lon, lat = gdf.geometry.centroid.x.mean(), gdf.geometry.centroid.y.mean()
    crs_utm = pyproj.CRS(
        f"EPSG:{pyproj.CRS.from_proj(pyproj.Proj(proj='latlong', datum='WGS84')).to_proj4().split(' ')[-1]}")
    gdf = gdf.to_crs(crs_utm.to_epsg())
    return gdf


def extract_files(uploaded_file, temp_dir):
    """Extrai arquivos de um ZIP ou RAR e retorna o caminho dos arquivos extraídos."""
    if uploaded_file.name.endswith('.zip'):
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    else:
        raise ValueError("Formato de arquivo não suportado. Por favor, envie um arquivo ZIP.")

    return [os.path.join(temp_dir, f) for f in os.listdir(temp_dir)]


def plot_shapefile(shapefile_path):
    """Plota o shapefile usando geopandas e matplotlib."""
    gdf = gpd.read_file(shapefile_path)
    # Cria o gráfico
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, color='lightblue', edgecolor='black')
    plt.title('Visualização do Arquivo')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    st.pyplot(fig)


def calculate_axes_lengths(shapefile_path):
    """Calcula os comprimentos dos eixos norte-sul e leste-oeste de um shapefile."""
    # Carregar o shapefile
    gdf = gpd.read_file(shapefile_path)

    # Verificar se o CRS é UTM para medidas precisas em metros
    gdf = ensure_utm_crs(gdf)

    # Obter as coordenadas de limite (bounding box)
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]

    # Cálculo dos comprimentos dos eixos
    length_ns = bounds[3] - bounds[1]  # Diferença de coordenadas Y (norte-sul)
    length_ew = bounds[2] - bounds[0]  # Diferença de coordenadas X (leste-oeste)

    # Retornar as coordenadas dos eixos e seus comprimentos
    axes_info = {
        #'Eixo norte-sul\n ': {'min_y': bounds[1], 'max_y': bounds[3],
        'comprimento em y': f'{length_ns}',
        #'Eixo leste-oeste\n': {'min_x': bounds[0], 'max_x': bounds[2],
        'comprimento em x': f'{length_ew}'
    }

    return axes_info


def plot_shapefile_with_axes(shapefile_path):
    """Plota o shapefile com os eixos norte-sul e leste-oeste passando pelo centróide."""
    # Carregar o shapefile
    gdf = gpd.read_file(shapefile_path)

    # Garantir que o CRS esteja em UTM para medidas precisas
    gdf = ensure_utm_crs(gdf)

    # Obter os limites do shapefile
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]

    # Calcular os comprimentos dos eixos
    length_ns, length_ew = bounds[3] - bounds[1], bounds[2] - bounds[0]

    # Calcular o centróide do shapefile
    centroid = gdf.geometry.centroid.unary_union

    # Coordenadas dos eixos baseadas no centróide
    mid_x, mid_y = centroid.x, centroid.y

    # Criar o gráfico
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, color='lightblue', edgecolor='black')

    # Plotar o eixo norte-sul (linha vertical)
    ns_line = mlines.Line2D([mid_x, mid_x], [bounds[1], bounds[3]], color='red', linestyle='--', label='Eixo Norte-Sul')
    ax.add_line(ns_line)

    # Plotar o eixo leste-oeste (linha horizontal)
    ew_line = mlines.Line2D([bounds[0], bounds[2]], [mid_y, mid_y], color='blue', linestyle='--',
                            label='Eixo Leste-Oeste')
    ax.add_line(ew_line)

    # Ajustar a visualização
    plt.title('Visualização do Arquivo com Eixos pelo Centróide')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.grid(False)
    st.pyplot(fig)

#######


def plot_shapefile_with_grids(gdf, reg_line_spacing, cross_line_spacing):
    """Plota o shapefile com linhas regulares e de verificação dentro da área do polígono e uma linha de contorno."""
    # Verificar se o input é uma string e carregar o GeoDataFrame se necessário
    if isinstance(gdf, str):
        gdf = gpd.read_file(gdf)

    # Garantir que o CRS esteja em UTM para medidas precisas
    gdf = ensure_utm_crs(gdf)

    # Criar a linha de contorno com um buffer de 10 metros para dentro
    gdf_contour = gdf.copy()
    gdf_contour['geometry'] = gdf_contour.buffer(-10)

    # Obter os limites do shapefile
    bounds = gdf_contour.total_bounds  # [minx, miny, maxx, maxy]

    # Criar GeoDataFrames para as linhas
    grid_lines = []

    # Criar linhas regulares (verticais)
    current_x = bounds[0]
    while current_x <= bounds[2]:
        line = LineString([(current_x, bounds[1]), (current_x, bounds[3])])
        grid_lines.append(line)
        current_x += cross_line_spacing

    # Criar linhas de verificação (horizontais)
    current_y = bounds[1]
    while current_y <= bounds[3]:
        line = LineString([(bounds[0], current_y), (bounds[2], current_y)])
        grid_lines.append(line)
        current_y += reg_line_spacing

    # Criar GeoDataFrame para as linhas de grid
    gdf_grid_lines = gpd.GeoDataFrame(geometry=grid_lines, crs=gdf.crs)

    # Realizar a interseção para garantir que as linhas de grid fiquem dentro do contorno com buffer
    gdf_grid_lines = gpd.overlay(gdf_grid_lines, gdf_contour, how='intersection')

    # Salvar os shapefiles modificados em um diretório temporário
    temp_dir = tempfile.mkdtemp()
    try:
        # Shapefile das linhas de grid
        grid_lines_shapefile_path = os.path.join(temp_dir, "shapefile_linhas_grid.shp")
        gdf_grid_lines.to_file(grid_lines_shapefile_path)

        # Shapefile do contorno
        contour_shapefile_path = os.path.join(temp_dir, "shapefile_contorno.shp")
        gdf_contour.to_file(contour_shapefile_path)

        # Exibir o gráfico
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax, color='lightblue', edgecolor='black')
        gdf_grid_lines.plot(ax=ax, color='red', linestyle='-', label='Linhas de Sondagem')
        gdf_contour.boundary.plot(ax=ax, color='purple', linewidth=1, label='Contorno do reservatório')

        plt.title('Visualização do Arquivo com Linhas de Sondagem e Contorno')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.legend()
        plt.grid(False)
        st.pyplot(fig)

        return temp_dir, [grid_lines_shapefile_path, contour_shapefile_path]  # Retorna o diretório e os caminhos dos arquivos shapefiles
    except Exception as e:
        st.error(f"Erro ao criar shapefiles: {e}")
        return None, None


def create_zip_from_directory(directory_path, zip_name):
    """Cria um arquivo zip a partir de um diretório."""
    zip_path = shutil.make_archive(zip_name, 'zip', directory_path)
    return zip_path


def download_shapefile_as_zip(temp_dir, file_paths):
    """Disponibiliza o shapefile processado como um arquivo ZIP para download."""
    zip_name = "shapefiles"
    zip_path = create_zip_from_directory(temp_dir, zip_name)
    with open(zip_path, "rb") as f:
        st.download_button(label="Baixar Shapefile Processado", data=f.read(), file_name=f"{zip_name}.zip", mime="application/zip")

    # Não remover o diretório temporário até que o download seja concluído
    return