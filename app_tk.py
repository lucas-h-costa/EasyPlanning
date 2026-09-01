# app_tk.py
import customtkinter as ctk
from tkinter import filedialog, messagebox, Text, Scrollbar
from tkinter.font import Font
import tempfile
import os
import functions_tk as f
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import tkintermapview
import geopandas as gpd
from shapely.geometry import Polygon, LineString

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class EasyPlanningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyPlanning ")
        self.root.geometry("1300x850")
        
        try:
            import os
            import tempfile
            diretorio_atual = os.path.dirname(os.path.abspath(__file__))
            caminho_icone = os.path.join(diretorio_atual, "pageIcon.jpg")
            
            # Abre a imagem JPG
            icone_img = Image.open(caminho_icone)
            
            # Salva temporariamente como .ico para forçar a substituição do ícone do CustomTkinter
            caminho_ico = os.path.join(tempfile.gettempdir(), "pageIcon_temp.ico")
            icone_img.save(caminho_ico, format="ICO", sizes=[(64, 64)])
            
            # Aplica o ícone nativo na barra de título
            self.root.iconbitmap(caminho_ico)
            
        except Exception as e:
            print(f"Não foi possível carregar o ícone: {e}")
            
        self.gdf_area = None
        self.gdf_eixo = None
        self.gdf_ls = None
        self.gdf_lv = None
        self.pdf_gerado = None
        self.entradas = {}
        
        self.modo_vetor = None
        self.coords_borda = []
        self.coords_eixo = []
        self.poly_borda = None
        self.path_eixo = None
        self.marcadores_vetor = []
        
        self.configurar_interface()

    def configurar_interface(self):
        barra_superior = ctk.CTkFrame(self.root, height=60, corner_radius=0, fg_color="#1f538d")
        barra_superior.pack(side='top', fill='x')
        
        ctk.CTkLabel(barra_superior, text="EasyPlanning GPHidro", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(side='left', padx=20, pady=10)
        
        ctk.CTkButton(barra_superior, text="Sobre", command=self.exibir_sobre, width=80, fg_color="#14375e", corner_radius=0).pack(side='right', padx=10, pady=10)
        ctk.CTkButton(barra_superior, text="Ajuda", command=self.exibir_ajuda, width=80, fg_color="#14375e", corner_radius=0).pack(side='right', padx=5, pady=10)
        ctk.CTkButton(barra_superior, text="Carregar Eixo", command=self.carregar_eixo, fg_color="#22c55e", hover_color="#16a34a", corner_radius=0).pack(side='right', padx=5, pady=10)
        ctk.CTkButton(barra_superior, text="Carregar Borda", command=self.carregar_borda, fg_color="#22c55e", hover_color="#16a34a", corner_radius=0).pack(side='right', padx=5, pady=10)

        self.abas = ctk.CTkTabview(self.root, corner_radius=0)
        self.abas.pack(fill='both', expand=True, padx=10, pady=10)
        aba_calc = self.abas.add("Parâmetros e Cálculos")
        self.aba_vetor = self.abas.add("Vetorizar área")

        coluna_esquerda = ctk.CTkFrame(aba_calc, corner_radius=0)
        coluna_esquerda.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        ctk.CTkLabel(coluna_esquerda, text="Métricas Espaciais", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        coluna_central = ctk.CTkFrame(aba_calc, corner_radius=0)
        coluna_central.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        ctk.CTkLabel(coluna_central, text="Configuração de Método", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        coluna_direita = ctk.CTkFrame(aba_calc, corner_radius=0)
        coluna_direita.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        ctk.CTkLabel(coluna_direita, text="Visualização e Saídas", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        self.variaveis = {
            'area_m2': ctk.DoubleVar(value=0.0),
            'comp_eixo_m': ctk.DoubleVar(value=0.0),
            'v_nos': ctk.DoubleVar(value=4.0),
            't_g_min': ctk.DoubleVar(value=2.0),
            'aplicar_buffer': ctk.BooleanVar(value=False),
            'buffer_m': ctk.DoubleVar(value=10.0),
            'metodo': ctk.StringVar(value="ANA_UHE"),
            'h_media': ctk.DoubleVar(value=10.0),
            'theta': ctk.DoubleVar(value=120.0),
            'c_mb': ctk.DoubleVar(value=100.0),
            'escala': ctk.DoubleVar(value=1000.0),
            'delta_manual': ctk.DoubleVar(value=20.0),
            'r_sss': ctk.DoubleVar(value=50.0),
            'alpha_sss': ctk.DoubleVar(value=10.0),
            'm_lv': ctk.DoubleVar(value=10.0),
            'n_s': ctk.IntVar(value=0)
        }

        self.variaveis['metodo'].trace_add('write', self.atualizar_estado_campos)
        self.variaveis['aplicar_buffer'].trace_add('write', self.atualizar_estado_buffer)

        self.adicionar_campo(coluna_esquerda, "Área Total (m²):", self.variaveis['area_m2'], 'area_m2')
        self.adicionar_campo(coluna_esquerda, "Comprimento do Eixo (m):", self.variaveis['comp_eixo_m'], 'comp_eixo_m')
        self.adicionar_campo(coluna_esquerda, "Velocidade da embarcação (nós):", self.variaveis['v_nos'], 'v_nos')
        self.adicionar_campo(coluna_esquerda, "Tempo transição tg (min):", self.variaveis['t_g_min'], 't_g_min')
        
        frame_buf = ctk.CTkFrame(coluna_esquerda, fg_color="transparent", corner_radius=0)
        frame_buf.pack(fill='x', padx=5, pady=(15, 5))
        ctk.CTkCheckBox(frame_buf, text="Aplicar Margem de Recuo (Buffer Interno)", variable=self.variaveis['aplicar_buffer'], command=self.atualizar_estado_buffer, corner_radius=0).pack(anchor='w', padx=10, pady=5)
        self.adicionar_campo(frame_buf, "Distância do Recuo (m):", self.variaveis['buffer_m'], 'buffer_m')

        opcoes_metodo = ["ANA_UHE", "ANA_PCH", "NORMAM_Monofeixe", "NORMAM_Multifeixe", "Escala", "Manual", "Side Scan (Cobertura 100%)", "Side Scan (Cobertura 200%)", "Side Scan (Cobertura > 200%)"]
        combo = ctk.CTkComboBox(coluna_central, variable=self.variaveis['metodo'], values=opcoes_metodo, command=self.atualizar_estado_campos, corner_radius=0)
        combo.pack(fill='x', padx=15, pady=5)
        
        self.adicionar_campo(coluna_central, "Profundidade média h (m):", self.variaveis['h_media'], 'h_media')
        self.adicionar_campo(coluna_central, "Abertura angular theta (°):", self.variaveis['theta'], 'theta')
        self.adicionar_campo(coluna_central, "Cobertura MBES C_MB (%):", self.variaveis['c_mb'], 'c_mb')
        self.adicionar_campo(coluna_central, "Denominador da Escala (E):", self.variaveis['escala'], 'escala')
        self.adicionar_campo(coluna_central, "Espaçamento Manual LS (m):", self.variaveis['delta_manual'], 'delta_manual')
        self.adicionar_campo(coluna_central, "Range SSS R (m):", self.variaveis['r_sss'], 'r_sss')
        self.adicionar_campo(coluna_central, "Altitude relativa SSS alpha (%):", self.variaveis['alpha_sss'], 'alpha_sss')
        self.adicionar_campo(coluna_central, "Multiplicador de Verificação (m LV):", self.variaveis['m_lv'], 'm_lv')

        ctk.CTkButton(coluna_central, text="Executar Cálculos e Gerar Linhas", command=self.processar_calculos, fg_color="#1f538d", height=40, corner_radius=0).pack(pady=25, fill='x', padx=15)

        self.botao_exportar = ctk.CTkButton(coluna_direita, text="Exportar Resultados", state='disabled', command=self.exportar_pacote, text_color = "white", fg_color="#1f538d", height=40, corner_radius=0)
        self.botao_exportar.pack(side='bottom', pady=10, fill='x', padx=5)
        
        self.frame_dashboard = ctk.CTkFrame(coluna_direita, fg_color="#1c1d1d", corner_radius=0)
        self.frame_dashboard.pack(side='bottom', fill='x', padx=5, pady=5)
        
        self.frame_mapa = ctk.CTkFrame(coluna_direita, fg_color="#ffffff", corner_radius=0)
        self.frame_mapa.pack(side='top', fill='both', expand=True, padx=5, pady=5)
        
        self.variaveis_dash = {
            'metodo': ctk.StringVar(value="-"),
            'ls': ctk.StringVar(value="-"),
            'lv': ctk.StringVar(value="-"),
            'seg': ctk.StringVar(value="-"),
            'tempo': ctk.StringVar(value="-")
        }
        
        self.criar_quadro_dashboard(self.frame_dashboard, "Método", self.variaveis_dash['metodo'], 0, 0)
        self.criar_quadro_dashboard(self.frame_dashboard, "Δ LS (m)", self.variaveis_dash['ls'], 0, 1)
        self.criar_quadro_dashboard(self.frame_dashboard, "Δ LV (m)", self.variaveis_dash['lv'], 0, 2)
        self.criar_quadro_dashboard(self.frame_dashboard, "Segmentos", self.variaveis_dash['seg'], 1, 0, columnspan=2)
        self.criar_quadro_dashboard(self.frame_dashboard, "Tempo (h)", self.variaveis_dash['tempo'], 1, 2)

        self.atualizar_estado_campos()
        self.atualizar_estado_buffer()

        frame_vetor_ctrl = ctk.CTkFrame(self.aba_vetor, width=220, corner_radius=0)
        frame_vetor_ctrl.pack(side='left', fill='y', padx=8, pady=8)
        
        ctk.CTkLabel(frame_vetor_ctrl, text="Controles de Desenho", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        ctk.CTkButton(frame_vetor_ctrl, text="Desenhar Borda", command=self.set_modo_borda, fg_color="#1f538d", corner_radius=0).pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(frame_vetor_ctrl, text="Desenhar Eixo", command=self.set_modo_eixo, fg_color="#1f538d", corner_radius=0).pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(frame_vetor_ctrl, text="Limpar Mapa", command=self.limpar_mapa_vetor, fg_color="#ef4444", hover_color="#dc2626", corner_radius=0).pack(fill='x', padx=10, pady=25)
        
        ctk.CTkLabel(frame_vetor_ctrl, text="Exportar arquivos", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        ctk.CTkButton(frame_vetor_ctrl, text="Salvar Borda (KML/JSON)", command=self.exportar_borda_kml, fg_color="#22c55e", hover_color="#16a34a", corner_radius=0).pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(frame_vetor_ctrl, text="Salvar Eixo (KML/JSON)", command=self.exportar_eixo_kml, fg_color="#22c55e", hover_color="#16a34a", corner_radius=0).pack(fill='x', padx=10, pady=5)

        self.map_widget = tkintermapview.TkinterMapView(self.aba_vetor, corner_radius=0)
        self.map_widget.pack(side='right', fill='both', expand=True, padx=8, pady=8)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(-20.7621, -42.8690)
        self.map_widget.set_zoom(15)
        self.map_widget.add_left_click_map_command(self.adicionar_ponto_mapa)

    def set_modo_borda(self):
        self.modo_vetor = 'borda'
        messagebox.showinfo("Modo Borda", "Clique no mapa para desenhar os vértices do polígono da borda.")

    def set_modo_eixo(self):
        self.modo_vetor = 'eixo'
        messagebox.showinfo("Modo Eixo", "Clique no mapa para desenhar a linha do eixo principal.")

    def adicionar_ponto_mapa(self, coords):
        if self.modo_vetor == 'borda':
            self.coords_borda.append(coords)
            if self.poly_borda:
                self.poly_borda.delete()
            if len(self.coords_borda) >= 3:
                self.poly_borda = self.map_widget.set_polygon(self.coords_borda, outline_color="#0ea5e9", fill_color="#e0f2fe", border_width=2)
        elif self.modo_vetor == 'eixo':
            self.coords_eixo.append(coords)
            if self.path_eixo:
                self.path_eixo.delete()
            if len(self.coords_eixo) >= 2:
                self.path_eixo = self.map_widget.set_path(self.coords_eixo, color="red", width=2)
        
        if self.modo_vetor:
            marc = self.map_widget.set_marker(coords[0], coords[1], marker_color_circle="#0a4f94", marker_color_outside="white")
            self.marcadores_vetor.append(marc)

    def limpar_mapa_vetor(self):
        self.coords_borda.clear()
        self.coords_eixo.clear()
        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_polygon()
        self.map_widget.delete_all_path()
        self.poly_borda = None
        self.path_eixo = None

    def exportar_borda_kml(self):
        if len(self.coords_borda) < 3:
            messagebox.showwarning("Aviso de Vetorização", "O polígono da borda precisa ser formado por pelo menos 3 pontos.")
            return
        caminho = filedialog.asksaveasfilename(defaultextension=".kml", filetypes=[("KML", "*.kml"), ("GeoJSON", "*.geojson")])
        if caminho:
            try:
                poly = Polygon([(lon, lat) for lat, lon in self.coords_borda])
                # Correção: Estruturar os dados com chaves em string
                gdf = gpd.GeoDataFrame({'Feicao': ['Borda_Vetorizada']}, geometry=[poly], crs="EPSG:4326")
                driver = "KML" if caminho.endswith(".kml") else "GeoJSON"
                gdf.to_file(caminho, driver=driver, engine="pyogrio")
                messagebox.showinfo("Exportação Concluída", f"Borda vetorizada e exportada com sucesso para:\n{caminho}")
            except Exception as e:
                messagebox.showerror("Falha na Exportação", f"Erro ao processar arquivo geográfico: {e}")

    def exportar_eixo_kml(self):
        if len(self.coords_eixo) < 2:
            messagebox.showwarning("Aviso de Vetorização", "A linha do eixo precisa ser formada por pelo menos 2 pontos.")
            return
        caminho = filedialog.asksaveasfilename(defaultextension=".kml", filetypes=[("KML", "*.kml"), ("GeoJSON", "*.geojson")])
        if caminho:
            try:
                linha = LineString([(lon, lat) for lat, lon in self.coords_eixo])
                # Correção: Estruturar os dados com chaves em string
                gdf = gpd.GeoDataFrame({'Feicao': ['Eixo_Vetorizado']}, geometry=[linha], crs="EPSG:4326")
                driver = "KML" if caminho.endswith(".kml") else "GeoJSON"
                gdf.to_file(caminho, driver=driver, engine="pyogrio")
                messagebox.showinfo("Exportação Concluída", f"Eixo vetorizado e exportado com sucesso para:\n{caminho}")
            except Exception as e:
                messagebox.showerror("Falha na Exportação", f"Erro ao processar arquivo geográfico: {e}")
    def adicionar_campo(self, conteiner, rotulo, variavel, chave):
        ctk.CTkLabel(conteiner, text=rotulo).pack(anchor='w', padx=15, pady=(2,0))
        entrada = ctk.CTkEntry(conteiner, textvariable=variavel, corner_radius=0)
        entrada.pack(fill='x', padx=15)
        self.entradas[chave] = entrada

    def atualizar_estado_buffer(self, *args):
        estado = 'normal' if self.variaveis['aplicar_buffer'].get() else 'disabled'
        self.entradas['buffer_m'].configure(state=estado)

    def atualizar_estado_campos(self, *args):
        metodo = self.variaveis['metodo'].get()
        
        campos_especificos = ['h_media', 'theta', 'c_mb', 'escala', 'delta_manual', 'r_sss', 'alpha_sss']
        for campo in campos_especificos:
            self.entradas[campo].configure(state='disabled')
            
        if metodo == 'NORMAM_Monofeixe':
            self.entradas['h_media'].configure(state='normal')
        elif metodo == 'NORMAM_Multifeixe':
            self.entradas['h_media'].configure(state='normal')
            self.entradas['theta'].configure(state='normal')
            self.entradas['c_mb'].configure(state='normal')
        elif metodo == 'Escala':
            self.entradas['escala'].configure(state='normal')
        elif metodo == 'Manual':
            self.entradas['delta_manual'].configure(state='normal')
        elif metodo in ['Side Scan (Cobertura 100%)', 'Side Scan (Cobertura 200%)']:
            self.entradas['r_sss'].configure(state='normal')
        elif metodo == 'Side Scan (Cobertura > 200%)':
            self.entradas['r_sss'].configure(state='normal')
            self.entradas['alpha_sss'].configure(state='normal')

    def criar_quadro_dashboard(self, conteiner, titulo, variavel, linha, coluna, columnspan=1):
        quadro = ctk.CTkFrame(conteiner, fg_color="#1a1a1a", corner_radius=0, border_width=1, border_color="#5c7186")
        quadro.grid(row=linha, column=coluna, columnspan=columnspan, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(quadro, text=titulo, font=ctk.CTkFont(size=11, weight="bold"), text_color="#a0a0a0").pack(anchor="center", pady=(4, 0))
        ctk.CTkLabel(quadro, textvariable=variavel, font=ctk.CTkFont(size=14, weight="bold"), text_color="#3a7ebf").pack(anchor="center", pady=(0, 4))
        conteiner.grid_columnconfigure(coluna, weight=1)

    def carregar_borda(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos Geográficos", "*.zip *.kml *.geojson")])
        if caminho:
            with tempfile.TemporaryDirectory() as dir_temp:
                try:
                    self.gdf_area = f.carregar_e_projetar(caminho, dir_temp)
                    area_total = self.gdf_area.geometry.area.sum()
                    self.variaveis['area_m2'].set(round(area_total, 2))
                    self.avaliar_geometrias_carregadas()
                    messagebox.showinfo("Arquivo carregado", f"Borda processada com CRS {self.gdf_area.crs.name}. Área calculada.")
                except Exception as erro:
                    messagebox.showerror("Erro", str(erro))

    def carregar_eixo(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos Geográficos", "*.zip *.kml *.geojson")])
        if caminho:
            with tempfile.TemporaryDirectory() as dir_temp:
                try:
                    self.gdf_eixo = f.carregar_e_projetar(caminho, dir_temp)
                    comprimento_total = self.gdf_eixo.geometry.length.sum()
                    self.variaveis['comp_eixo_m'].set(round(comprimento_total, 2))
                    self.avaliar_geometrias_carregadas()
                    messagebox.showinfo("Arquivo carregado", f"Eixo processado com CRS {self.gdf_eixo.crs.name}. Comprimento calculado.")
                except Exception as erro:
                    messagebox.showerror("Erro", str(erro))

    def avaliar_geometrias_carregadas(self):
        if self.gdf_area is not None and self.gdf_eixo is not None:
            if self.gdf_area.crs != self.gdf_eixo.crs:
                self.gdf_eixo = self.gdf_eixo.to_crs(self.gdf_area.crs)
            largura_efetiva = f.calcular_largura_perpendicular(self.gdf_area, self.gdf_eixo)
            if largura_efetiva > 0:
                messagebox.showinfo("Estimativa Transversal", f"Largura transversal estimada para a área: {largura_efetiva:.2f} m.")

    def processar_calculos(self):
        try:
            if self.gdf_area is None or self.gdf_eixo is None:
                messagebox.showwarning("Geometrias Ausentes", "Carregue os arquivos de Borda e Eixo antes de executar.")
                return

            metodo_selecionado = self.variaveis['metodo'].get()
            delta_ls, delta_lv = f.calcular_espacamentos(
                area_m2=self.variaveis['area_m2'].get(),
                comp_eixo_m=self.variaveis['comp_eixo_m'].get(),
                metodo=metodo_selecionado,
                h=self.variaveis['h_media'].get(),
                theta=self.variaveis['theta'].get(),
                c_mb=self.variaveis['c_mb'].get(),
                escala=self.variaveis['escala'].get(),
                delta_manual=self.variaveis['delta_manual'].get(),
                r_sss=self.variaveis['r_sss'].get(),
                alpha=self.variaveis['alpha_sss'].get(),
                m_lv=self.variaveis['m_lv'].get()
            )
            
            aplicar_buf = self.variaveis['aplicar_buffer'].get()
            val_buf = self.variaveis['buffer_m'].get()

            self.gdf_ls, self.gdf_lv = f.gerar_linhas(
                self.gdf_area, self.gdf_eixo, delta_ls, delta_lv, aplicar_buf, val_buf
            )
            
            fig = f.gerar_grafico(
                self.gdf_area, self.gdf_eixo, self.gdf_ls, self.gdf_lv, aplicar_buf, val_buf
            )
            
            for widget in self.frame_mapa.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.frame_mapa)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            if delta_ls > 0:
                qnt_linhas = max(1, int(self.variaveis['comp_eixo_m'].get() / delta_ls))
                self.variaveis['n_s'].set(qnt_linhas)
            
            l_tot_estimado = self.variaveis['comp_eixo_m'].get()
            tempo_horas = f.calcular_estimativa_tempo(
                l_tot_m=l_tot_estimado * (self.variaveis['n_s'].get() if delta_ls > 0 else 1),
                v_nos=self.variaveis['v_nos'].get(),
                t_g_min=self.variaveis['t_g_min'].get(),
                n_s=self.variaveis['n_s'].get()
            )

            self.variaveis_dash['metodo'].set(metodo_selecionado.replace("_", " "))
            self.variaveis_dash['ls'].set(f"{delta_ls:.2f}")
            self.variaveis_dash['lv'].set(f"{delta_lv:.2f}")
            self.variaveis_dash['seg'].set(str(self.variaveis['n_s'].get()))
            self.variaveis_dash['tempo'].set(f"{tempo_horas:.2f}")

            dicionario_resultados = {
                "CRS": self.gdf_area.crs.name if self.gdf_area.crs else "Desconhecido",
                "Área Total da Borda": f"{self.variaveis['area_m2'].get():.2f} m²",
                "Comprimento Total do Eixo": f"{self.variaveis['comp_eixo_m'].get():.2f} m",
                "Buffer Interno": f"{val_buf:.2f} m" if aplicar_buf else "Não aplicado",
                "Método de Cálculo Aplicado": metodo_selecionado.replace("_", " "),
                "Velocidade de Navegação": f"{self.variaveis['v_nos'].get():.1f} nós"
            }
            
            if metodo_selecionado in ['NORMAM_Monofeixe', 'NORMAM_Multifeixe']:
                dicionario_resultados["Profundidade Média (h)"] = f"{self.variaveis['h_media'].get():.2f} m"
            if metodo_selecionado == 'NORMAM_Multifeixe':
                dicionario_resultados["Abertura Angular (θ)"] = f"{self.variaveis['theta'].get():.1f}°"
                dicionario_resultados["Cobertura (C_MB)"] = f"{self.variaveis['c_mb'].get():.1f}%"
            if metodo_selecionado == 'Escala':
                dicionario_resultados["Escala do Levantamento (E)"] = f"1:{self.variaveis['escala'].get():.0f}"
            if metodo_selecionado == 'Manual':
                dicionario_resultados["Espaçamento LS Manual (Δ_LS)"] = f"{self.variaveis['delta_manual'].get():.2f} m"
            if 'Side Scan' in metodo_selecionado:
                dicionario_resultados["Alcance SSS (Range)"] = f"{self.variaveis['r_sss'].get():.2f} m"
            if metodo_selecionado == 'Side Scan (Cobertura > 200%)':
                dicionario_resultados["Altitude Relativa (α)"] = f"{self.variaveis['alpha_sss'].get():.1f}%"

            dicionario_resultados.update({
                "Multiplicador de Verificação": f"{self.variaveis['m_lv'].get():.1f}",
                "Espaçamento LS Geométrico (Δ_LS)": f"{delta_ls:.2f} m",
                "Espaçamento LV Geométrico (Δ_LV)": f"{delta_lv:.2f} m",
                "Quantidade de Segmentos Projetados": f"{self.variaveis['n_s'].get()} linhas",
                "Tempo Operacional Estimado": f"{tempo_horas:.2f} horas"
            })

            self.pdf_gerado = f.gerar_relatorio_pdf(dicionario_resultados, fig)
            self.botao_exportar.configure(state='normal')

        except Exception as excecao_calculo:
            messagebox.showerror("Interrupção Crítica", f"Falha na execução matemática ou espacial: {excecao_calculo}")

    def exportar_pacote(self):
        if self.pdf_gerado:
            diretorio = filedialog.askdirectory(title="Selecione a pasta para exportação do Pacote")
            if diretorio:
                caminho_pdf = os.path.join(diretorio, "Relatorio_Planejamento.pdf")
                with open(caminho_pdf, 'wb') as arquivo_saida:
                    arquivo_saida.write(self.pdf_gerado)
                
                if self.gdf_ls is not None and not self.gdf_ls.empty:
                    caminho_ls_json = os.path.join(diretorio, "Linhas_Sondagem.geojson")
                    caminho_ls_csv = os.path.join(diretorio, "Linhas_Sondagem.csv")
                    self.gdf_ls.to_file(caminho_ls_json, driver="GeoJSON", engine="pyogrio")
                    f.exportar_geometria_csv(self.gdf_ls, caminho_ls_csv, "LS_")
                    
                if self.gdf_lv is not None and not self.gdf_lv.empty:
                    caminho_lv_json = os.path.join(diretorio, "Linhas_Verificacao.geojson")
                    caminho_lv_csv = os.path.join(diretorio, "Linhas_Verificacao.csv")
                    self.gdf_lv.to_file(caminho_lv_json, driver="GeoJSON", engine="pyogrio")
                    f.exportar_geometria_csv(self.gdf_lv, caminho_lv_csv, "LV_")
                    
                messagebox.showinfo("Exportação Concluída", "Pacote exportado com sucesso no diretório selecionado. Vetores salvos em formatos GeoJSON e CSV.")

    def exibir_ajuda(self):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_manual = os.path.join(diretorio_atual, "manual.md")
        
        try:
            with open(caminho_manual, "r", encoding="utf-8") as arquivo:
                conteudo = arquivo.read()
        except Exception as e:
            conteudo = f"Erro ao tentar carregar o manual: {e}"

        janela_ajuda = ctk.CTkToplevel(self.root)
        janela_ajuda.title("Manual do Usuário")
        janela_ajuda.geometry("1000x750")
        janela_ajuda.transient(self.root)
        
        try:
            janela_ajuda.iconbitmap(self.root.wm_iconbitmap())
        except Exception:
            pass

        # Frame para conter o Text e Scrollbar
        frame_texto = ctk.CTkFrame(janela_ajuda, corner_radius=0, fg_color="#1a1a1a")
        frame_texto.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Usar tkinter.Text padrão para melhor suporte a formatação
        caixa_texto = Text(
            frame_texto,
            wrap="word",
            bg="#1a1a1a",
            fg="#e0e0e0",
            insertbackground="#1f9fe8",
            selectbackground="#1f538d"
        )
        
        scrollbar = Scrollbar(frame_texto, command=caixa_texto.yview)
        caixa_texto.config(yscrollcommand=scrollbar.set)
        
        caixa_texto.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar tags de estilo com fontes
        fonte_h1 = Font(family="Segoe UI", size=16, weight="bold")
        fonte_h2 = Font(family="Segoe UI", size=13, weight="bold")
        fonte_body = Font(family="Segoe UI", size=11)
        fonte_bold = Font(family="Segoe UI", size=11, weight="bold")
        fonte_italic = Font(family="Segoe UI", size=11, slant="italic")
        
        caixa_texto.tag_config("h1", font=fonte_h1, foreground="#1f9fe8", spacing1=12, spacing3=12)
        caixa_texto.tag_config("h2", font=fonte_h2, foreground="#60a5fa", spacing1=8, spacing3=8)
        caixa_texto.tag_config("body", font=fonte_body, foreground="#e0e0e0", spacing3=8)
        caixa_texto.tag_config("bold", font=fonte_bold, foreground="#ffffff")
        caixa_texto.tag_config("italic", font=fonte_italic, foreground="#d0d0d0")
        
        # Processar linhas e renderizar
        linhas = conteudo.split('\n')
        i = 0
        while i < len(linhas):
            linha = linhas[i]
            
            # Títulos nível 1
            if linha.startswith('# ') and not linha.startswith('## '):
                titulo = linha[2:].strip()
                caixa_texto.insert("end", titulo + "\n", "h1")
                i += 1
            # Títulos nível 2
            elif linha.startswith('## '):
                titulo = linha[3:].strip()
                caixa_texto.insert("end", titulo + "\n", "h2")
                i += 1
            # Linhas vazias
            elif linha.strip() == "":
                caixa_texto.insert("end", "\n")
                i += 1
            # Parágrafos normais
            else:
                paragrafo = linha.strip()
                if paragrafo:
                    # Renderizar com suporte a formatação básica
                    self._renderizar_paragrafo(caixa_texto, paragrafo)
                    caixa_texto.insert("end", "\n")
                i += 1
                
        caixa_texto.configure(state="disabled")

    def _renderizar_paragrafo(self, widget, texto):
        """Renderiza um parágrafo com suporte a **negrito** e *itálico*"""
        import re
        
        # Padrão para detectar **negrito** e *itálico*
        matches = []
        for match in re.finditer(r'\*\*([^*]+)\*\*|\*([^*]+)\*', texto):
            matches.append((match.start(), match.end(), match.group(0)))
        
        matches.sort(key=lambda x: x[0])
        
        ultima_pos = 0
        for inicio, fim, match_str in matches:
            # Inserir texto antes da correspondência
            if inicio > ultima_pos:
                widget.insert("end", texto[ultima_pos:inicio], "body")
            
            # Processar a correspondência
            if match_str.startswith('**') and match_str.endswith('**'):
                conteudo = match_str[2:-2]
                widget.insert("end", conteudo, "bold")
            elif match_str.startswith('*') and match_str.endswith('*'):
                conteudo = match_str[1:-1]
                widget.insert("end", conteudo, "italic")
            
            ultima_pos = fim
        
        # Inserir texto restante
        if ultima_pos < len(texto):
            widget.insert("end", texto[ultima_pos:], "body")

    def exibir_sobre(self):
        messagebox.showinfo("Sobre o Sistema", "EasyPlanning - Módulo de Planejamento Hidrográfico\nVersão 1.0\nDesenvolvido por Lucas H. Costa\n2026")

if __name__ == "__main__":
    raiz = ctk.CTk()
    aplicacao = EasyPlanningApp(raiz)
    raiz.mainloop()