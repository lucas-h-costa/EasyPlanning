import tkinter as tk
from tkinter import Canvas, messagebox
import numpy as np
from tkinter import PhotoImage


def calculate():
    try:
        max_length = float(entry_max_length.get())
        min_length = float(entry_min_length.get())
        average_depth = float(entry_average_depth.get())
        sonar_range = float(entry_range.get())
        sound_speed = float(entry_sound_speed.get())
        velocity = float(entry_velocity.get())
        beam_width = float(entry_beam_width.get())
        desired_coverage = float(entry_coverage.get())
        selected_value = selected_option.get()
        velocity_m_s = velocity / 1.944

        if beam_width == 0 or beam_width == '':
            beam_width = 8

        if sound_speed == 0 or sound_speed == '':
            sound_speed = 1500

        ping_rate = (2 * average_depth) / sound_speed  # Cálculo do ping rate
        ping_rate_hz = 1 / ping_rate  # em Hertz -> achar formula para alterar ping rate de acordo com a velocidade da embarcação

        area = float(max_length * min_length)

        sonar_footprint = 2 * average_depth * np.tan(np.radians(beam_width / 2)) # Cálculo do footprint
        reg_line_spacing = 0
        cross_line_spacing = 0

        if selected_value == 'Normam':
            reg_line_spacing = 3 * average_depth
            desired_coverage = 5
            if reg_line_spacing > 25:
                reg_line_spacing = 25
            cross_line_spacing = 10 * reg_line_spacing

        elif selected_value == 'ANA-UHE':
            reg_line_spacing = (0.35 * (area / 10000) ** 0.35) / (max_length / 1000)
            cross_line_spacing = 3 * reg_line_spacing

        elif selected_value == 'ANA-PCE':
            reg_line_spacing = (0.1 * (area / 10000) ** 0.25) / (max_length / 1000)
            cross_line_spacing = 3 * reg_line_spacing

        if cross_line_spacing >= min_length:
            cross_line_spacing = min_length / 2

        total_reg_lines = round(max_length / reg_line_spacing)
        total_cross_lines = round(min_length / cross_line_spacing)

        survey_time = round(((total_reg_lines * min_length + total_cross_lines * max_length) / velocity_m_s)/60)
        unit = 'minutos'

        if survey_time >= 60:
            survey_time = round(survey_time / 60)
            unit = 'horas'
        total_time = round(survey_time * 1.25)

        label_area_result.config(text=f'{area:.2f} m²')
        label_ping_rate_result.config(text=f'{ping_rate_hz:.2f} Hertz')
        label_reg_line_spacing_result.config(text=f'{reg_line_spacing:.2f} m')
        label_cross_line_spacing_result.config(text=f'{cross_line_spacing:.2f} m')
        label_survey_time_result.config(text=f'{survey_time:.1f} {unit}')
        label_total_time_result.config(text=f'{total_time:.1f} {unit}')
        draw_footprint(sonar_footprint, desired_coverage)  # Desenho do footprint

    except ValueError:
        messagebox.showerror("Erro de entrada", "Por favor, insira valores válidos.")


def draw_footprint(sonar_footprint, desired_coverage):
    canvas.delete("all")
    diameter = sonar_footprint * 20
    spacing = diameter * (1 - desired_coverage / 100)
    for i in range(5):
        canvas.create_oval(50 + i * (diameter + spacing), 50, 50 + i * (diameter + spacing) + diameter, 50 + diameter,
                           outline="darkblue", width=3)
    canvas.create_text(50 + diameter / 2, 50 + diameter + 10, text="\nPegada do sonar", fill="black",
                       font="Arial 14 bold", anchor="center")


def about():
    messagebox.showinfo("Sobre", "Software para planejamento de campanhas batimétricas desenvolvido pelo GPHIDRRO (Grupo de Pesquisa em Hidrografia)\nVersão 1.0")


def max_length(event):
    messagebox.showinfo('Comprimento máximo', 'Comprimento, em metros, da maior feição da área a ser levantada.')


def min_length(event):
    messagebox.showinfo('Comprimento mínimo', 'Comprimento, em metros, da menor feição da área a ser levantada.')


def average_depth(event):
    messagebox.showinfo('Profundidade média', 'Profundidade média estimada da área a ser levantada.')


def sonar_range(event):
    messagebox.showinfo('Alcance do sonar', 'Insira o alcance configurado do sonar em metros.')


def beam_width(event):
    messagebox.showinfo('Largura de feixe do sonar', 'Insira a largura de feixe do seu sonar, em graus. Por padrão será adotado o valor de 8°.')


def sound_speed(event):
    messagebox.showinfo('Velocidade do som na água', 'Insira a velocidade média obtida do som na água, em m/s. Por padrão, será adotado o valor de 1500 m/s.')


def coverage(event):
    messagebox.showinfo('Cobertura desejada', 'Porcentagem de cobertura desejada para o levantamento da área\n100% corresponde à toda a área sendo ensonificada uma única vez, sem sobreposição.')


def velocity(event):
    messagebox.showinfo('Velocidade da embarcação', 'Insira a velocidade da embarcação em nós.')

def norma(event):
    new_window = tk.Toplevel(janela)
    new_window.title('Escolha a norma que deseja seguir')

    text = tk.Text(new_window, wrap=tk.WORD)
    text.insert(tk.END, 'Esolha a norma que deseja seguir:\n\n Normam 501: Marinha do Brasil\n\n'
                                                            'ANA-UHE: Agência Nacional de Águas e Saneamento Básico - Usinas Hidrelétricas\n\n'
                                                            'ANA-PCE: Agência Nacional de Águas e Saneamento Básico - Pequenas Centrais Hidrelétricas\n\n')

    text.config(state=tk.DISABLED)
    text.pack(expand=True, fill='both', padx=10, pady=10)

    # Define a janela como não redimensionável
    new_window.resizable(False, False)

def help_window():
    new_window = tk.Toplevel(janela)
    new_window.title('Ajuda')

    text = tk.Text(new_window, wrap=tk.WORD)
    text.insert(tk.END, 'Para calcular o planejamento de campanhas batimétricas, insira os valores solicitados e clique em "Calcular".\n\n'
                        'Comprimento máximo da área (m): Comprimento, em metros, da maior feição da área a ser levantada.\n\n'
                        'Comprimento mínimo da área (m): Comprimento, em metros, da menor feição da área a ser levantada.\n\n'
                        'Profundidade média da área (m): Profundidade média estimada da área a ser levantada.\n\n'
                        'Alcance do sonar (m): Insira o alcance configurado do sonar em metros.\n\n'
                        'Velocidade do som na água (m/s): Insira a velocidade média obtida do som na água, em m/s. Por padrão, será adotado o valor de 1500 m/s.\n\n'
                        'Velocidade da embarcação (nós): Insira a velocidade da embarcação em nós.\n\n'
                        'Largura de feixe (graus): Insira a largura de feixe do seu sonar, em graus. Por padrão será adotado o valor de 8°.\n\n'
                        '% de cobertura desejada: Porcentagem de cobertura desejada para o levantamento da área\n100% corresponde à toda a área sendo ensonificada uma única vez, sem sobreposição.\n\n'
                        'Selecione a norma: Selecione a norma que deseja seguir.\n\n'
                        'Clique em "Calcular" para obter os resultados.\n\n'
                        'Clique em "Sobre" para mais informações sobre o software.\n\n'
                        'Clique em "Ajuda" para obter informações sobre o uso do software.\n\n'
                        'Clique em "Sair" para fechar o software.\n\n')

    text.config(state=tk.DISABLED)
    text.pack(expand=True, fill='both', padx=10, pady=10)


def out():
    janela.quit()


# Criação da janela principal
janela = tk.Tk()
janela.title("GPHIDRO Calculator")
icon = PhotoImage(file='icon.png')
janela.iconphoto(False, icon)
janela.configure(bg= 'lightblue')
canvas = Canvas(janela, width=800, height=200)  # Criação do Canvas

selected_option = tk.StringVar()
options = ["Normam", "ANA-UHE", "ANA-PCE"]
selected_option.set(options[0])

# Criação da barra de menu
menu_bar = tk.Menu(janela)

# Menu 'Arquivo'
menu_arquivo = tk.Menu(menu_bar, tearoff=0)
menu_arquivo.add_command(label='Sobre', command=about)
menu_arquivo.add_separator()
menu_arquivo.add_command(label="Sair", command=out)
menu_arquivo.add_command(label="Ajuda", command=help_window)
menu_bar.add_cascade(label="Arquivo", menu=menu_arquivo)

# Adiciona a barra de menu à janela
janela.config(menu=menu_bar)

# Criação dos widgets
label_max_length = tk.Label(janela, text="Comprimento máximo da área (m):", bg='lightblue')
entry_max_length = tk.Entry(janela)
label_max_length.bind("<Button-1>", max_length)

label_min_length = tk.Label(janela, text="Comprimento mínimo da área (m):",bg='lightblue')
entry_min_length = tk.Entry(janela)
label_min_length.bind("<Button-1>", min_length)

label_average_depth = tk.Label(janela, text="Profundidade média da área (m):",bg='lightblue')
entry_average_depth = tk.Entry(janela)
label_average_depth.bind("<Button-1>", average_depth)

label_range = tk.Label(janela, text="Alcance do sonar (m):",bg='lightblue')
entry_range = tk.Entry(janela)
label_range.bind("<Button-1>", sonar_range)

label_sound_speed = tk.Label(janela, text="Velocidade do som na água (m/s):",bg='lightblue')
entry_sound_speed = tk.Entry(janela)
label_sound_speed.bind("<Button-1>", sound_speed)

label_velocity = tk.Label(janela, text="Velocidade da embarcação (nós):",bg='lightblue')
entry_velocity = tk.Entry(janela)
label_velocity.bind("<Button-1>", velocity)

label_beam_width = tk.Label(janela, text="Largura de feixe (graus):",bg='lightblue')
entry_beam_width = tk.Entry(janela)
label_beam_width.bind("<Button-1>", beam_width)

label_coverage = tk.Label(janela, text="% de cobertura desejada:",bg='lightblue')
entry_coverage = tk.Entry(janela)
label_coverage.bind("<Button-1>", coverage)

label_area = tk.Label(janela, text="Área total do levantamento:",bg='lightblue')
label_area_result = tk.Label(janela, text="",bg='lightblue')

label_ping_rate = tk.Label(janela, text="Ping Rate Máximo recomendado:",bg='lightblue')
label_ping_rate_result = tk.Label(janela, text="",bg='lightblue')

label_reg_line_spacing = tk.Label(janela, text="Espaçamento das linhas regulares de sondagem:",bg='lightblue')
label_reg_line_spacing_result = tk.Label(janela, text="",bg='lightblue')

label_cross_line_spacing = tk.Label(janela, text="Espaçamento das linhas de verificação:",bg='lightblue')
label_cross_line_spacing_result = tk.Label(janela, text="",bg='lightblue')

label_survey_time = tk.Label(janela, text="Tempo estimado para levantamento das linhas:",bg='lightblue')
label_survey_time_result = tk.Label(janela, text="",bg='lightblue')

label_total_time = tk.Label(janela, text="Tempo total estimado para o levantamento:",bg='lightblue')
label_total_time_result = tk.Label(janela, text="",bg='lightblue')

label_calculated_coverage = tk.Label(janela, text="Cobertura calculada:",bg='lightblue')
label_calculated_coverage_result = tk.Label(janela, text="")

label_calculated_overlap = tk.Label(janela, text="Sobreposição calculada:",bg='lightblue')
label_calculated_overlap_result = tk.Label(janela, text="",bg='lightblue')

# Posicionamento dos widgets
label_max_length.grid(row=0, column=0, sticky=tk.W)
entry_max_length.grid(row=0, column=1)

label_min_length.grid(row=1, column=0, sticky=tk.W)
entry_min_length.grid(row=1, column=1)

label_average_depth.grid(row=2, column=0, sticky=tk.W)
entry_average_depth.grid(row=2, column=1)

label_range.grid(row=3, column=0, sticky=tk.W)
entry_range.grid(row=3, column=1)

label_sound_speed.grid(row=4, column=0, sticky=tk.W)
entry_sound_speed.grid(row=4, column=1)

label_velocity.grid(row=5, column=0, sticky=tk.W)
entry_velocity.grid(row=5, column=1)

label_beam_width.grid(row=6, column=0, sticky=tk.W)
entry_beam_width.grid(row=6, column=1)

label_coverage.grid(row=7, column=0, sticky=tk.W)
entry_coverage.grid(row=7, column=1)

# Criação do frame para os botões
button_frame = tk.Frame(janela)

# Criação e posicionamento dos botões dentro do frame
option_menu = tk.OptionMenu(button_frame, selected_option, *options)
option_menu.grid(row=0, column=0)
option_menu.bind("<Button-3>", norma)
button_calcular = tk.Button(button_frame, text="Calcular", command=calculate)
button_calcular.grid(row=0, column=1)

# Posicionamento do frame na janela
button_frame.grid(row=8, column=0, columnspan=2)

label_area.grid(row=9, column=0, sticky=tk.W)
label_area_result.grid(row=9, column=1)

label_ping_rate.grid(row=10, column=0, sticky=tk.W)
label_ping_rate_result.grid(row=10, column=1)

label_reg_line_spacing.grid(row=11, column=0, sticky=tk.W)
label_reg_line_spacing_result.grid(row=11, column=1)

label_cross_line_spacing.grid(row=12, column=0, sticky=tk.W)
label_cross_line_spacing_result.grid(row=12, column=1)

label_survey_time.grid(row=13, column=0, sticky=tk.W)
label_survey_time_result.grid(row=13, column=1)

label_total_time.grid(row=14, column=0, sticky=tk.W)
label_total_time_result.grid(row=14, column=1)


canvas.grid(row=18, columnspan=2)  # Posicionamento do Canvas
canvas.configure(bg='lightblue')
# Início do loop principal
janela.mainloop()
