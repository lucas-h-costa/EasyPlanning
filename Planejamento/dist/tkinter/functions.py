import geopandas as gpd
import zipfile
import rarfile
import tempfile
import os
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Image

def set_default_values(beam_width, sound_speed, average_depth, max_length, min_length, sonar_range):
    """Define valores padrão se não forem fornecidos."""
    if beam_width is None:
        beam_width = 8
    if sound_speed is None:
        sound_speed = 1500
    if average_depth is None:
        average_depth = 10
    if max_length is None:
        max_length = 1000
    if min_length is None:
        min_length = 100
    if sonar_range is None:
        sonar_range = 10
    return beam_width, sound_speed, average_depth, max_length, min_length, sonar_range

def calculate_ping_rate(sonar_range, sound_speed, frequency):
    """Calcula a taxa de ping a partir do alcance do sonar e da velocidade do som."""
    frequency_hz = frequency * 1000
    double_range = 2 * sonar_range
    ping_rate = (double_range / sound_speed) + 2 * (10 / frequency_hz)
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

def calculate_survey_time(reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines, min_length,
                          max_length, nav_speed, contour_length):
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

def line_spacing(area, max_length, min_length, selected_option, average_depth):
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

    if cross_line_spacing >= min_length / 2:
        cross_line_spacing = min_length / 3

    total_reg_lines = round(max_length / reg_line_spacing)
    total_cross_lines = round(min_length / cross_line_spacing)
    return reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines

def draw_footprint(coverage_percentage, root):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    diameter = 10
    spacing = diameter * (1 - coverage_percentage / 100)  # Calcula o espaçamento com base na porcentagem de cobertura

    for i in range(5):
        circle = plt.Circle((10 + i * (diameter + spacing), 90), diameter / 2, edgecolor='red', facecolor='none', lw=1)
        ax.add_patch(circle)

    ax.set_xlim(0, 50 + 5 * (diameter + spacing))
    ax.set_ylim(0, 100)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Desativa os eixos

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def open_shapefile(file_path):
    """Abre e processa o shapefile, tratando diferentes formatos de compressão."""
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == ".zip":
        with zipfile.ZipFile(file_path, "r") as z:
            with tempfile.TemporaryDirectory() as temp_dir:
                z.extractall(temp_dir)
                shapefile_path = next((os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".shp")), None)
                if shapefile_path:
                    return gpd.read_file(shapefile_path)
    elif file_ext == ".rar":
        with rarfile.RarFile(file_path, "r") as r:
            with tempfile.TemporaryDirectory() as temp_dir:
                r.extractall(temp_dir)
                shapefile_path = next((os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".shp")), None)
                if shapefile_path:
                    return gpd.read_file(shapefile_path)
    else:
        return gpd.read_file(file_path)

def calculate_contour_length(geo_df):
    """Calcula o comprimento total do contorno no shapefile."""
    geo_df["contour_length"] = geo_df.length
    return geo_df["contour_length"].sum()

def generate_pdf_report(results):
    """Gera um relatório PDF com os resultados."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))

    elements = []

    title = Paragraph("Relatório de Campanha Batimétrica", styles['Title'])
    elements.append(title)

    subtitle = Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal'])
    elements.append(subtitle)

    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    table_data = [[key, str(value)] for key, value in results.items()]

    table = Table(table_data, colWidths=[3 * inch, 3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    footer = Paragraph("Relatório gerado automaticamente.", styles['Normal'])
    elements.append(footer)

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data
