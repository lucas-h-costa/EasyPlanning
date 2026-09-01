import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import zipfile
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from shapely.geometry import LineString

def carregar_e_projetar(file_path, temp_dir):
    if file_path.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        arquivos = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.shp')]
        if not arquivos:
            raise ValueError("Nenhum Shapefile encontrado no arquivo ZIP.")
        alvo = arquivos[0]
    elif file_path.endswith('.kml') or file_path.endswith('.geojson'):
        alvo = file_path
    else:
        raise ValueError("Formato de arquivo não suportado. Utilize ZIP (SHP), KML ou GeoJSON.")

    gdf = gpd.read_file(alvo, engine="pyogrio")
    if gdf.crs is None or gdf.crs.is_geographic:
        gdf = gdf.to_crs(gdf.estimate_utm_crs())
    return gdf

def calcular_largura_perpendicular(gdf_area, gdf_eixo):
    try:
        poligono = gdf_area.geometry.unary_union
        eixo = gdf_eixo.geometry.unary_union
        ponto_medio = eixo.interpolate(0.5, normalized=True)
        p1 = eixo.interpolate(0.49, normalized=True)
        p2 = eixo.interpolate(0.51, normalized=True)
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        linha_perpendicular = LineString([
            (ponto_medio.x - 500000 * dy, ponto_medio.y + 500000 * dx),
            (ponto_medio.x + 500000 * dy, ponto_medio.y - 500000 * dx)
        ])
        intersecao = linha_perpendicular.intersection(poligono)
        if not intersecao.is_empty:
            return intersecao.length
        return 0.0
    except Exception as e:
        print(f"Falha no cálculo geométrico transversal: {e}")
        return 0.0

def calcular_espacamentos(area_m2, comp_eixo_m, metodo, h, theta, c_mb, escala, delta_manual, r_sss, alpha, m_lv):
    a_ha = area_m2 / 10000.0
    l_km = comp_eixo_m / 1000.0
    if l_km == 0:
        return 0.0, 0.0

    if metodo == 'ANA_UHE':
        delta_ls = (0.35 * (a_ha ** 0.35) / l_km) * 1000.0
    elif metodo == 'ANA_PCH':
        delta_ls = (0.1 * (a_ha ** 0.25) / l_km) * 1000.0
    elif metodo == 'NORMAM_Monofeixe':
        delta_ls = np.ceil(max(3.0 * h, 25.0))
    elif metodo == 'NORMAM_Multifeixe':
        theta_rad = np.radians(theta)
        w = 2.0 * h * np.tan(theta_rad / 2.0)
        delta_ls = np.ceil(1.5 * w - w * (c_mb / 200.0))
    elif metodo == 'Escala':
        delta_ls = 0.005 * escala
    elif metodo == 'Manual':
        delta_ls = delta_manual
    elif metodo == 'Side Scan (Cobertura 100%)':
        delta_ls = 2.0 * r_sss
    elif metodo == 'Side Scan (Cobertura 200%)':
        delta_ls = r_sss
    elif metodo == 'Side Scan (Cobertura > 200%)':
        delta_ls = r_sss * (1.0 - (alpha / 100.0))
    else:
        delta_ls = 0.0

    delta_lv = m_lv * delta_ls
    return delta_ls, delta_lv

def calcular_estimativa_tempo(l_tot_m, v_nos, t_g_min, n_s):
    if v_nos <= 0:
        return 0.0
    horas = (l_tot_m / (v_nos * 1852.0)) + ((t_g_min / 60.0) * max(0, n_s - 1))
    return horas

def gerar_linhas(gdf_area, gdf_eixo, delta_ls, delta_lv, aplicar_buffer=False, valor_buffer=0.0):
    area_geom = gdf_area.geometry.unary_union
    
    # Aplicação de buffer interno (recuo)
    if aplicar_buffer and valor_buffer > 0:
        area_recorte = area_geom.buffer(-valor_buffer)
        if area_recorte.is_empty:
            raise ValueError("O valor do buffer é maior que a dimensão do polígono, resultando em área vazia.")
    else:
        area_recorte = area_geom

    eixo = gdf_eixo.geometry.unary_union
    linhas_ls = []
    linhas_lv = []
    
    if delta_ls > 0:
        distancias = np.arange(0, eixo.length, delta_ls)
        for d in distancias:
            p_atual = eixo.interpolate(d)
            p_ant = eixo.interpolate(max(0, d - 0.1))
            p_prox = eixo.interpolate(min(eixo.length, d + 0.1))
            if p_prox.equals(p_ant):
                continue
            dx = p_prox.x - p_ant.x
            dy = p_prox.y - p_ant.y
            norma = (dx**2 + dy**2)**0.5
            if norma == 0:
                continue
            nx, ny = -dy/norma, dx/norma
            linha_infinita = LineString([
                (p_atual.x - 500000 * nx, p_atual.y - 500000 * ny),
                (p_atual.x + 500000 * nx, p_atual.y + 500000 * ny)
            ])
            intersecao = linha_infinita.intersection(area_recorte)
            if not intersecao.is_empty:
                linhas_ls.append(intersecao)
                
    if delta_lv > 0:
        intersecao_central = eixo.intersection(area_recorte)
        if not intersecao_central.is_empty:
            linhas_lv.append(intersecao_central)
        multiplicador = 1
        while True:
            try:
                offset_esq = eixo.offset_curve(multiplicador * delta_lv)
                offset_dir = eixo.offset_curve(-multiplicador * delta_lv)
            except AttributeError:
                offset_esq = eixo.parallel_offset(multiplicador * delta_lv, 'left')
                offset_dir = eixo.parallel_offset(multiplicador * delta_lv, 'right')
            
            inter_esq = offset_esq.intersection(area_recorte) if not offset_esq.is_empty else None
            inter_dir = offset_dir.intersection(area_recorte) if not offset_dir.is_empty else None
            
            adicionou = False
            if inter_esq and not inter_esq.is_empty:
                linhas_lv.append(inter_esq)
                adicionou = True
            if inter_dir and not inter_dir.is_empty:
                linhas_lv.append(inter_dir)
                adicionou = True
                
            if not adicionou:
                break
            multiplicador += 1
            
    gdf_ls = gpd.GeoDataFrame(geometry=linhas_ls, crs=gdf_area.crs) if linhas_ls else None
    gdf_lv = gpd.GeoDataFrame(geometry=linhas_lv, crs=gdf_area.crs) if linhas_lv else None
    return gdf_ls, gdf_lv

def gerar_grafico(gdf_area, gdf_eixo, gdf_ls, gdf_lv, aplicar_buffer=False, valor_buffer=0.0):
    fig, ax = plt.subplots(figsize=(6, 5))
    
    fig.suptitle("Planta de Linhas Projetadas", fontsize=12, fontweight='bold')
    
    if gdf_area is not None:
        if gdf_area.crs:
            ax.set_title(f"Projeção: {gdf_area.crs.name}", fontsize=9, color='#5c7186', pad=10)
        gdf_area.plot(ax=ax, color='#e0f2fe', edgecolor='#0ea5e9', alpha=0.6, label='Área de Estudo')
        if aplicar_buffer and valor_buffer > 0:
            area_buf = gdf_area.geometry.unary_union.buffer(-valor_buffer)
            if not area_buf.is_empty:
                gpd.GeoSeries([area_buf]).boundary.plot(ax=ax, color='#0284c7', linewidth=1.2, linestyle=':', label=f'Recuo ({valor_buffer}m)')
        
    if gdf_eixo is not None:
        gdf_eixo.plot(ax=ax, color='black', linewidth=1.5, linestyle='--', label='Eixo Principal')
    if gdf_ls is not None and not gdf_ls.empty:
        gdf_ls.plot(ax=ax, color='#ef4444', linewidth=1, label='Linhas de Sondagem')
    if gdf_lv is not None and not gdf_lv.empty:
        gdf_lv.plot(ax=ax, color='#22c55e', linewidth=1.5, label='Linhas de Verificação')
    
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_xticks([])
    ax.set_yticks([])
    
    manuseios, rotulos = ax.get_legend_handles_labels()
    if manuseios:
        ax.legend(manuseios, rotulos, loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize='small', frameon=False)
        
    plt.tight_layout()
    return fig

def gerar_relatorio_pdf(resultados, fig, titulo="Relatório Técnico de Planejamento"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        leftMargin=0.5*inch, 
        rightMargin=0.5*inch, 
        topMargin=0.5*inch, 
        bottomMargin=0.5*inch
    )
    elementos = []
    estilos = getSampleStyleSheet()
    
    estilo_titulo_cabecalho = ParagraphStyle(
        'TituloCabecalho', parent=estilos['Normal'], fontName='Helvetica-Bold', 
        fontSize=15, textColor=colors.white, leading=18
    )
    estilo_sub_cabecalho = ParagraphStyle(
        'SubCabecalho', parent=estilos['Normal'], fontName='Helvetica', 
        fontSize=10, textColor=colors.HexColor("#e0f2fe"), leading=14
    )
    estilo_secao = ParagraphStyle(
        'Secao', parent=estilos['Normal'], fontName='Helvetica-Bold', 
        fontSize=11, textColor=colors.HexColor("#0b5aa2"), spaceBefore=14, spaceAfter=6
    )

    tabela_cabecalho_conteudo = [
        [Paragraph("Relatório Técnico de Planejamento Hidrográfico", estilo_titulo_cabecalho)],
        [Paragraph("EasyPlanning, GPHIDRO, UFV", estilo_sub_cabecalho)],
        [Paragraph(f"Gerado automaticamente em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", estilo_sub_cabecalho)]
    ]
    tabela_cabecalho = Table(tabela_cabecalho_conteudo, colWidths=[7.5*inch])
    tabela_cabecalho.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#0b5aa2")),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
    ]))
    elementos.append(tabela_cabecalho)
    
    # 1. Dados Espaciais
    elementos.append(Paragraph("1. Dados Espaciais", estilo_secao))
    dados_espaciais = [
        ["Sistema de Referência (CRS)", resultados.get("CRS", "Desconhecido")],
        ["Área Total da Borda", resultados.get("Área Total da Borda", "-")],
        ["Comprimento Total do Eixo", resultados.get("Comprimento Total do Eixo", "-")],
        ["Buffer Interno (Recuo)", resultados.get("Buffer Interno", "Não aplicado")]
    ]
    tabela_espaciais = Table(dados_espaciais, colWidths=[2.5*inch, 5.0*inch])
    tabela_espaciais.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#eef5fb")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#d7d7d7")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elementos.append(tabela_espaciais)
    
    # 2. Critérios e Parâmetros Operacionais
    elementos.append(Paragraph("2. Critérios e Parâmetros Operacionais", estilo_secao))
    dados_operacionais = [
        ["Método de Cálculo", resultados.get("Método de Cálculo Aplicado", "-")],
        ["Velocidade de Navegação", resultados.get("Velocidade de Navegação", "-")],
        ["Espaçamento Linhas de Sondagem (LS)", resultados.get("Espaçamento LS Geométrico (Δ_LS)", "-")],
        ["Espaçamento Linhas de Verificação (LV)", resultados.get("Espaçamento LV Geométrico (Δ_LV)", "-")],
        ["Multiplicador de Verificação", resultados.get("Multiplicador de Verificação", "-")],
        ["Total de Segmentos Projetados", resultados.get("Quantidade de Segmentos Projetados", "-")],
        ["Tempo Operacional Estimado", resultados.get("Tempo Operacional Estimado", "-")]
    ]
    
    # Inserção condicional de parâmetros de sensores caso existam
    if "Profundidade Média (h)" in resultados:
        dados_operacionais.insert(2, ["Profundidade Média (h)", resultados["Profundidade Média (h)"]])
    if "Abertura Angular (θ)" in resultados:
        dados_operacionais.insert(3, ["Abertura Angular (θ)", resultados["Abertura Angular (θ)"]])
    if "Cobertura (C_MB)" in resultados:
        dados_operacionais.insert(4, ["Cobertura Multifeixe (C_MB)", resultados["Cobertura (C_MB)"]])
    if "Escala do Levantamento (E)" in resultados:
        dados_operacionais.insert(2, ["Escala da Carta (E)", resultados["Escala do Levantamento (E)"]])
    if "Espaçamento LS Manual (Δ_LS)" in resultados:
        dados_operacionais.insert(2, ["Espaçamento Manual Definido", resultados["Espaçamento LS Manual (Δ_LS)"]])
    if "Alcance SSS (Range)" in resultados:
        dados_operacionais.insert(2, ["Alcance Lateral SSS (Range)", resultados["Alcance SSS (Range)"]])
    if "Altitude Relativa (α)" in resultados:
        dados_operacionais.insert(3, ["Altitude Relativa SSS (α)", resultados["Altitude Relativa (α)"]])

    tabela_operacionais = Table(dados_operacionais, colWidths=[2.5*inch, 5.0*inch])
    tabela_operacionais.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#eef5fb")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#d7d7d7")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elementos.append(tabela_operacionais)
    
    # 3. Representação Espacial
    elementos.append(Paragraph("3. Representação Espacial", estilo_secao))
    if fig is not None:
        buffer_img = BytesIO()
        fig.savefig(buffer_img, format='png', dpi=200, bbox_inches='tight')
        buffer_img.seek(0)
        img_pdf = Image(buffer_img, width=6.0*inch, height=4.2*inch, kind='proportional')
        elementos.append(img_pdf)
        
    doc.build(elementos)
    return buffer.getvalue()

def exportar_geometria_csv(gdf, caminho_arquivo, prefixo):
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write("nome da linha,E inicio,N inicio,E fim,N fim\n")
            for i, row in enumerate(gdf.itertuples()):
                if row.geometry.geom_type == 'LineString':
                    coords = list(row.geometry.coords)
                    if len(coords) >= 2:
                        x_ini, y_ini = coords[0][:2]
                        x_fim, y_fim = coords[-1][:2]
                        f.write(f"{prefixo}{i+1},{x_ini:.3f},{y_ini:.3f},{x_fim:.3f},{y_fim:.3f}\n")
                elif row.geometry.geom_type == 'MultiLineString':
                    for j, line in enumerate(row.geometry.geoms):
                        coords = list(line.coords)
                        if len(coords) >= 2:
                            x_ini, y_ini = coords[0][:2]
                            x_fim, y_fim = coords[-1][:2]
                            f.write(f"{prefixo}{i+1}_{j+1},{x_ini:.3f},{y_ini:.3f},{x_fim:.3f},{y_fim:.3f}\n")
    except Exception as e:
        print(f"Erro ao exportar CSV: {e}")