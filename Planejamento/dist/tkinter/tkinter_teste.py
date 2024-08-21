import tkinter as tk
from tkinter import filedialog, messagebox
from functions import open_shapefile, calculate_contour_length, set_default_values, calculate_ping_rate, \
    calculate_sonar_footprint, calculate_velocity, line_spacing, calculate_survey_time, draw_footprint, generate_pdf_report

def select_shapefile():
    file_path = filedialog.askopenfilename(
        filetypes=[("Shapefiles", "*.shp"), ("ZIP files", "*.zip"), ("RAR files", "*.rar")]
    )
    return file_path

def on_calculate():
    file_path = select_shapefile()
    if not file_path:
        messagebox.showwarning("Aviso", "Nenhum arquivo selecionado!")
        return

    try:
        geo_df = open_shapefile(file_path)  # Abre o shapefile
        contour_length = calculate_contour_length(geo_df)  # Calcula o comprimento do contorno
        beam_width, sound_speed, average_depth, max_length, min_length, sonar_range = set_default_values(
            None, None, None, None, None, None
        )
        ping_rate_hz = calculate_ping_rate(sonar_range, sound_speed, 200)  # Exemplo de frequência de 200 kHz
        sonar_footprint = calculate_sonar_footprint(beam_width, sonar_range)
        velocity_m_s, velocity_knots = calculate_velocity(sonar_footprint, ping_rate_hz)
        reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines = line_spacing(
            contour_length, max_length, min_length, "Normam", average_depth
        )
        survey_time, total_time, unit = calculate_survey_time(
            reg_line_spacing, cross_line_spacing, total_reg_lines, total_cross_lines, min_length, max_length,
            velocity_knots, contour_length
        )

        # Monta os resultados em um dicionário
        results = {
            "Comprimento da linha de contorno": contour_length,
            "Taxa de ping (Hz)": ping_rate_hz,
            "Pegada do sonar (m)": sonar_footprint,
            "Velocidade de navegação (m/s)": velocity_m_s,
            "Velocidade de navegação (nós)": velocity_knots,
            "Espaçamento das linhas regulares (m)": reg_line_spacing,
            "Espaçamento das linhas cruzadas (m)": cross_line_spacing,
            "Total de linhas regulares": total_reg_lines,
            "Total de linhas cruzadas": total_cross_lines,
            "Tempo de levantamento": f"{survey_time} {unit}",
            "Tempo total estimado": f"{total_time} {unit}"
        }

        # Chama a função para desenhar o gráfico da pegada do sonar
        draw_footprint(80, root)

        # Gera o relatório em PDF
        pdf_report = generate_pdf_report(results)
        with open("report.pdf", "wb") as f:
            f.write(pdf_report)
        messagebox.showinfo("Relatório", "Relatório PDF gerado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao processar o arquivo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Planejamento de Campanhas Batimétricas")

    calculate_button = tk.Button(root, text="Selecionar Shapefile e Calcular", command=on_calculate)
    calculate_button.pack(pady=20)

    root.mainloop()

