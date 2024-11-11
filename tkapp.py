import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkfunctions as f
import geopandas as gpd
import tempfile
import os

class EasyPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Easy Planning")
        self.create_widgets()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input fields
        ttk.Label(self.frame, text="Comprimento máximo da área (m):").grid(row=0, column=0, sticky=tk.W)
        self.max_length = ttk.Entry(self.frame)
        self.max_length.grid(row=0, column=1)

        ttk.Label(self.frame, text="Comprimento mínimo da área (m):").grid(row=1, column=0, sticky=tk.W)
        self.min_length = ttk.Entry(self.frame)
        self.min_length.grid(row=1, column=1)

        ttk.Label(self.frame, text="Profundidade média da área (m):").grid(row=2, column=0, sticky=tk.W)
        self.average_depth = ttk.Entry(self.frame)
        self.average_depth.grid(row=2, column=1)

        ttk.Label(self.frame, text="Velocidade de navegação (nós):").grid(row=3, column=0, sticky=tk.W)
        self.nav_speed = ttk.Entry(self.frame)
        self.nav_speed.grid(row=3, column=1)

        ttk.Label(self.frame, text="Alcance do sonar (m):").grid(row=4, column=0, sticky=tk.W)
        self.sonar_range = ttk.Entry(self.frame)
        self.sonar_range.grid(row=4, column=1)

        ttk.Label(self.frame, text="Velocidade do som na água (m/s):").grid(row=5, column=0, sticky=tk.W)
        self.sound_speed = ttk.Entry(self.frame)
        self.sound_speed.grid(row=5, column=1)

        ttk.Label(self.frame, text="Frequência do sonar (kHz):").grid(row=6, column=0, sticky=tk.W)
        self.frequency = ttk.Entry(self.frame)
        self.frequency.grid(row=6, column=1)

        ttk.Label(self.frame, text="Largura do feixe (graus):").grid(row=7, column=0, sticky=tk.W)
        self.beam_width = ttk.Entry(self.frame)
        self.beam_width.grid(row=7, column=1)

        ttk.Label(self.frame, text="Opção de espaçamento de linha:").grid(row=8, column=0, sticky=tk.W)
        self.selected_option = ttk.Combobox(self.frame, values=["Normam", "ANA-UHE", "ANA-PCH", "Escala", "Personalizado"])
        self.selected_option.grid(row=8, column=1)

        self.generate_cross_lines = tk.BooleanVar()
        ttk.Checkbutton(self.frame, text="Gerar Linhas de Verificação", variable=self.generate_cross_lines).grid(row=9, column=0, columnspan=2, sticky=tk.W)

        ttk.Button(self.frame, text="Calcular", command=self.calculate).grid(row=10, column=0, columnspan=2)

        self.results_text = tk.Text(self.frame, height=10, width=50)
        self.results_text.grid(row=11, column=0, columnspan=2)

        ttk.Button(self.frame, text="Upload de arquivo SHP", command=self.upload_shp).grid(row=12, column=0, columnspan=2)

    def calculate(self):
        try:
            max_length = float(self.max_length.get())
            min_length = float(self.min_length.get())
            average_depth = float(self.average_depth.get())
            nav_speed = float(self.nav_speed.get())
            sonar_range = float(self.sonar_range.get())
            sound_speed = float(self.sound_speed.get())
            frequency = float(self.frequency.get())
            beam_width = float(self.beam_width.get())
            selected_option = self.selected_option.get()
            generate_cross_lines = self.generate_cross_lines.get()

            area = max_length * min_length
            reg_line_spacing = 0
            cross_line_spacing = 0
            scale = 0

            results, sonar_footprint, pdf_file = f.calculate(max_length, min_length, area, average_depth, sonar_range,
                                                             sound_speed, beam_width, selected_option, generate_cross_lines, frequency,
                                                             reg_line_spacing, cross_line_spacing, scale, contour_length=0)

            self.results_text.delete(1.0, tk.END)
            if results:
                for key, value in results.items():
                    self.results_text.insert(tk.END, f"{key}: {value}\n")
            else:
                self.results_text.insert(tk.END, "Erro ao calcular.")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular: {e}")

    def upload_shp(self):
        file_path = filedialog.askopenfilename(filetypes=[("Shapefiles", "*.zip *.rar")])
        if file_path:
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    extracted_files = f.extract_files(file_path, temp_dir)
                    shapefiles = [f for f in extracted_files if f.endswith('.shp')]

                    if not shapefiles:
                        messagebox.showerror("Erro", "O arquivo comprimido não contém um shapefile (.shp).")
                    else:
                        shapefile_path = shapefiles[0]
                        gdf = gpd.read_file(shapefile_path)
                        total_area = gdf.geometry.area.sum()
                        gdf_contour = gdf.copy()
                        gdf_contour['geometry'] = gdf_contour.buffer(-10)
                        contour_length = gdf_contour.boundary.length.sum()
                        info = f.calculate_axes_lengths(shapefile_path)
                        messagebox.showinfo("Informação", f"Área total calculada: {total_area:.2f} m^2\n{info}")

                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EasyPlannerApp(root)
    root.mainloop()