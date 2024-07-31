
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Image
from io import BytesIO
from datetime import datetime
import streamlit as st
import geopandas as gpd
import pandas as pd
import zipfile
import rarfile
import tempfile
import os
import pyproj
from shapely.geometry import Polygon




def line_spacing(area, max_length, min_length, selected_option, average_depth):
    km = max_length / 1000
    hectares = area / 10000

    if selected_option == 'Normam':

        reg_line_spacing = min(3 * average_depth, 25)
        cross_line_spacing = 10 * reg_line_spacing

    elif selected_option == 'ANA-UHE':

        reg_line_spacing = (0.35 * (hectares ** 0.35)) / km
        cross_line_spacing = 3 * reg_line_spacing

    elif selected_option == 'ANA-PCH':

        reg_line_spacing = (0.1 * (hectares ** 0.25)) / km
        cross_line_spacing = 3 * reg_line_spacing

    if cross_line_spacing >= min_length:
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
    logo_path = "Planejamento/icon.png"
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
    table_data = [["Parâmetro", "Valor"]]  # Cabeçalho da tabela
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


def calculate_area_gauss(geometry):
    """Calcula a área usando o método de Gauss (fórmula de área de polígono)."""
    if geometry.is_empty:
        return 0.0

    coords = list(geometry.exterior.coords)
    x = [coord[0] for coord in coords]
    y = [coord[1] for coord in coords]

    n = len(x)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += x[i] * y[j]
        area -= x[j] * y[i]
    area = abs(area) / 2.0
    return area


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
    elif uploaded_file.name.endswith('.rar'):
        with rarfile.RarFile(uploaded_file, 'r') as rar_ref:
            rar_ref.extractall(temp_dir)
    else:
        raise ValueError("Formato de arquivo não suportado. Por favor, envie um arquivo ZIP ou RAR.")

    return [os.path.join(temp_dir, f) for f in os.listdir(temp_dir)]


def process_shapefile(shapefile_path):
    """Processa um arquivo shapefile e calcula a área total dos polígonos usando o método de Gauss."""
    gdf = gpd.read_file(shapefile_path, driver='ESRI Shapefile')
    gdf = ensure_utm_crs(gdf)  # Garantindo que o CRS esteja em UTM

    total_area = 0.0
    for geom in gdf.geometry:
        if geom.geom_type in ['Polygon', 'MultiPolygon']:
            # Se for MultiPolygon, itere sobre cada polígono
            if geom.geom_type == 'MultiPolygon':
                for polygon in geom:
                    total_area += calculate_area_gauss(polygon)
            else:
                total_area += calculate_area_gauss(geom)

    return total_area


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