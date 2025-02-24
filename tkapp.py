import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import geopandas as gpd
import functions as f  # Suas funções auxiliares
import tempfile

# Funções de ajuda e sobre
def ajuda():
    messagebox.showinfo("Ajuda", "Para calcular o planejamento de campanhas batimétricas, siga os seguintes passos:\n"
                                 "1. Insira os parâmetros de entrada.\n"
                                 "2. Clique no botão 'Calcular'.\n"
                                 "3. Os resultados serão exibidos na tela.")

def sobre():
    messagebox.showinfo("Sobre", "Easy Planning é uma aplicação para planejamento de campanhas batimétricas.\n"
                                 "Desenvolvido por Lucas Costa - Grupo de Pesquisa em Hidrografia - GPHIDRO.")

# Função de carregamento de arquivo
def carregar_arquivo_kml():
    filepath = filedialog.askopenfilename(filetypes=[("KML files", "*.kml")])
    if filepath:
        file_label.config(text=f"Arquivo selecionado: {filepath}")
    return filepath

# Função de cálculo de linhas
def calcular_linhas():
    try:
        max_length = float(entry_max_length.get())
        min_length = float(entry_min_length.get())
        average_depth = float(entry_avg_depth.get())
        sonar_range = float(entry_sonar_range.get())
        reg_line_spacing = float(entry_reg_line_spacing.get())
        cross_line_spacing = float(entry_cross_line_spacing.get())
        
        selected_option = combo_option.get()
        generate_cross_lines = var_cross_lines.get()

        area = max_length * min_length
        reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines = f.line_spacing(
            area, max_length, min_length, selected_option, average_depth, reg_line_spacing, cross_line_spacing, 0, generate_cross_lines)

        result_label.config(text=f"Espaçamento das linhas regulares de sondagem: {reg_line_spacing:.2f} m\n"
                                 f"Espaçamento das linhas de verificação: {cross_line_spacing:.2f} m\n"
                                 f"Total de linhas regulares de sondagem: {total_reg_lines}\n"
                                 f"Total de linhas de verificação: {total_cross_lines}")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante o cálculo: {str(e)}")

# Função para gerar sobreposição
def gerar_sobreposicao():
    try:
        coverage_percentage = float(entry_coverage.get())
        beam_width = float(entry_beam_width.get())
        nav_speed = float(entry_nav_speed.get())
        sonar_range = float(entry_sonar_range1.get())
        sound_speed = float(entry_sound_speed1.get())
        frequency = float(entry_frequency.get())

        ping_rate_hz = f.calculate_ping_rate(sonar_range, sound_speed, frequency)
        footprint = f.calculate_sonar_footprint(beam_width, sonar_range)
        overlap = f.calculate_overlap(footprint, sonar_range, nav_speed, ping_rate_hz)

        messagebox.showinfo("Resultado da Sobreposição", f"Pegada de cobertura do sonar: {footprint:.2f} m²\n"
                                                         f"Sobreposição calculada: {overlap:.2f} m")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Interface Tkinter
root = tk.Tk()
root.title("Easy Planning - Tkinter")
root.geometry("900x700")
root.configure(bg='#f0f0f0')

# Função para criar o menu superior
def create_menu():
    menu_bar = tk.Menu(root)
    
    # Menu "Arquivo"
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Carregar KML", command=carregar_arquivo_kml)
    file_menu.add_separator()
    file_menu.add_command(label="Sair", command=root.quit)
    menu_bar.add_cascade(label="Arquivo", menu=file_menu)

    # Menu "Ajuda"
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Ajuda", command=ajuda)
    help_menu.add_command(label="Sobre", command=sobre)
    menu_bar.add_cascade(label="Ajuda", menu=help_menu)

    root.config(menu=menu_bar)

# Função para organizar as entradas dentro de frames
def create_labeled_entry(parent, label_text, var):
    label = tk.Label(parent, text=label_text, anchor='w', bg='#f0f0f0')
    label.pack(fill='x', padx=10, pady=5)
    entry = tk.Entry(parent, textvariable=var)
    entry.pack(fill='x', padx=10, pady=5)
    return entry

# Criar Frames para o layout
frame_linhas = tk.Frame(root, bg='#f0f0f0')
frame_linhas.pack(padx=20, pady=10, fill='both', expand=True)

frame_sobreposicao = tk.Frame(root, bg='#f0f0f0')
frame_sobreposicao.pack(padx=20, pady=10, fill='both', expand=True)

# Seção de Planejamento de Linhas
tk.Label(frame_linhas, text="Planejamento de Linhas", font=("Arial", 18), bg='#f0f0f0').pack(pady=10)

entry_max_length = create_labeled_entry(frame_linhas, "Comprimento máximo da área (m):", tk.DoubleVar())
entry_min_length = create_labeled_entry(frame_linhas, "Comprimento mínimo da área (m):", tk.DoubleVar())
entry_avg_depth = create_labeled_entry(frame_linhas, "Profundidade média da área (m):", tk.DoubleVar())
entry_sonar_range = create_labeled_entry(frame_linhas, "Alcance do sonar (m):", tk.DoubleVar())

# Opções de espaçamento de linha
tk.Label(frame_linhas, text="Escolha uma opção de espaçamento de linha:", bg='#f0f0f0').pack(pady=5)
combo_option = ttk.Combobox(frame_linhas, values=["Normam", "ANA-UHE", "ANA-PCH", "Escala", "Personalizado"])
combo_option.pack(padx=10, pady=5)

# Checkbox para gerar linhas de verificação
var_cross_lines = tk.IntVar()
tk.Checkbutton(frame_linhas, text="Gerar Linhas de Verificação", variable=var_cross_lines, bg='#f0f0f0').pack(padx=10, pady=5)

entry_reg_line_spacing = create_labeled_entry(frame_linhas, "Espaçamento das linhas regulares de sondagem (m):", tk.DoubleVar())
entry_cross_line_spacing = create_labeled_entry(frame_linhas, "Espaçamento das linhas de verificação (m):", tk.DoubleVar())

# Botão para Planejar
tk.Button(frame_linhas, text="Planejar", command=calcular_linhas, bg='#007bff', fg='white').pack(pady=10)

# Label para resultados
result_label = tk.Label(frame_linhas, text="", bg='#f0f0f0')
result_label.pack(pady=10)

# Seção de Cálculo de Sobreposição
tk.Label(frame_sobreposicao, text="Cálculo de Sobreposição", font=("Arial", 18), bg='#f0f0f0').pack(pady=10)

entry_coverage = create_labeled_entry(frame_sobreposicao, "Porcentagem de cobertura (%):", tk.DoubleVar())
entry_beam_width = create_labeled_entry(frame_sobreposicao, "Largura do feixe do sonar (°):", tk.DoubleVar())
entry_nav_speed = create_labeled_entry(frame_sobreposicao, "Velocidade de navegação (nós):", tk.DoubleVar())
entry_sonar_range1 = create_labeled_entry(frame_sobreposicao, "Alcance do sonar (m):", tk.DoubleVar())
entry_sound_speed1 = create_labeled_entry(frame_sobreposicao, "Velocidade do som na água (m/s):", tk.DoubleVar())
entry_frequency = create_labeled_entry(frame_sobreposicao, "Frequência do sonar (kHz):", tk.DoubleVar())

# Botão para Gerar Sobreposição
tk.Button(frame_sobreposicao, text="Gerar Sobreposição", command=gerar_sobreposicao, bg='#28a745', fg='white').pack(pady=10)

# Label para o arquivo KML carregado
file_label = tk.Label(root, text="Nenhum arquivo KML carregado", bg='#f0f0f0')
file_label.pack(pady=10)

# Criar o menu superior
create_menu()

root.mainloop()
