import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tempfile
import os
import functions_tk as f
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
class EasyPlanningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyPlanning - Planejamento Hidrográfico")
        self.root.geometry("1300x850")
        try:
            icone_img = Image.open("pageIcon.jpg")
            self.icone_app = ImageTk.PhotoImage(icone_img)
            self.root.wm_iconphoto(True, self.icone_app)
        except Exception as e:
            print(f"Não foi possível carregar o ícone: {e}")
        self.gdf_area = None
        self.gdf_eixo = None
        self.gdf_ls = None
        self.gdf_lv = None
        self.pdf_gerado = None
        self.entradas = {}
        self.configurar_interface()

    def configurar_interface(self):
        barra_superior = tk.Frame(self.root, bg="#0a4f94", height=60)
        barra_superior.pack(side='top', fill='x')
        
        tk.Label(barra_superior, text="EasyPlanning GPHidro", font=('Segoe UI', 16, 'bold'), bg="#0a4f94", fg="white").pack(side='left', padx=20, pady=10)
        
        tk.Button(barra_superior, text="Sobre", command=self.exibir_sobre, bg="#0f6fc2", fg="white", relief='flat', font=('Segoe UI', 10, 'bold'), padx=15).pack(side='right', padx=10, pady=10)
        tk.Button(barra_superior, text="Ajuda", command=self.exibir_ajuda, bg="#0f6fc2", fg="white", relief='flat', font=('Segoe UI', 10, 'bold'), padx=15).pack(side='right', padx=5, pady=10)
        tk.Button(barra_superior, text="Carregar Eixo", command=self.carregar_eixo, bg="#22c55e", fg="white", relief='flat', font=('Segoe UI', 10, 'bold'), padx=15).pack(side='right', padx=5, pady=10)
        tk.Button(barra_superior, text="Carregar Borda", command=self.carregar_borda, bg="#22c55e", fg="white", relief='flat', font=('Segoe UI', 10, 'bold'), padx=15).pack(side='right', padx=5, pady=10)

        conteiner_principal = tk.Frame(self.root, bg="#f4f8fc")
        conteiner_principal.pack(fill='both', expand=True, padx=10, pady=10)

        coluna_esquerda = tk.LabelFrame(conteiner_principal, text="Métricas Espaciais e Operacionais", font=('Segoe UI', 10, 'bold'), bg="#ffffff")
        coluna_esquerda.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        coluna_central = tk.LabelFrame(conteiner_principal, text="Configuração de Método", font=('Segoe UI', 10, 'bold'), bg="#ffffff")
        coluna_central.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        coluna_direita = tk.LabelFrame(conteiner_principal, text="Visualização e Saídas", font=('Segoe UI', 10, 'bold'), bg="#ffffff")
        coluna_direita.pack(side='left', fill='both', expand=True, padx=8, pady=8)

        self.variaveis = {
            'area_m2': tk.DoubleVar(value=0.0),
            'comp_eixo_m': tk.DoubleVar(value=0.0),
            'v_nos': tk.DoubleVar(value=4.0),
            't_g_min': tk.DoubleVar(value=2.0),
            'aplicar_buffer': tk.BooleanVar(value=False),
            'buffer_m': tk.DoubleVar(value=10.0),
            'metodo': tk.StringVar(value="ANA_UHE"),
            'h_media': tk.DoubleVar(value=10.0),
            'theta': tk.DoubleVar(value=120.0),
            'c_mb': tk.DoubleVar(value=100.0),
            'escala': tk.DoubleVar(value=1000.0),
            'delta_manual': tk.DoubleVar(value=20.0),
            'r_sss': tk.DoubleVar(value=50.0),
            'alpha_sss': tk.DoubleVar(value=10.0),
            'm_lv': tk.DoubleVar(value=10.0),
            'n_s': tk.IntVar(value=0)
        }

        self.variaveis['metodo'].trace_add('write', self.atualizar_estado_campos)
        self.variaveis['aplicar_buffer'].trace_add('write', self.atualizar_estado_buffer)

        # Coluna Esquerda
        self.adicionar_campo(coluna_esquerda, "Área Total (m²):", self.variaveis['area_m2'], 'area_m2')
        self.adicionar_campo(coluna_esquerda, "Comprimento do Eixo (m):", self.variaveis['comp_eixo_m'], 'comp_eixo_m')
        self.adicionar_campo(coluna_esquerda, "Velocidade da embarcação (nós):", self.variaveis['v_nos'], 'v_nos')
        self.adicionar_campo(coluna_esquerda, "Tempo transição tg (min):", self.variaveis['t_g_min'], 't_g_min')
        
        # Grupo de Buffer (Recuo da Borda)
        frame_buf = tk.LabelFrame(coluna_esquerda, text="Margem de Recuo (Buffer)", font=('Segoe UI', 9, 'bold'), bg="#ffffff")
        frame_buf.pack(fill='x', padx=5, pady=(15, 5))
        tk.Checkbutton(frame_buf, text="Aplicar Buffer Interno", variable=self.variaveis['aplicar_buffer'], bg="#ffffff").pack(anchor='w', padx=5, pady=2)
        self.adicionar_campo(frame_buf, "Distância do Recuo (m):", self.variaveis['buffer_m'], 'buffer_m')

        # Coluna Central
        tk.Label(coluna_central, text="Método de Cálculo (LS):", bg="#ffffff").pack(anchor='w', padx=5, pady=(10,0))
        opcoes_metodo = ["ANA_UHE", "ANA_PCH", "NORMAM_Monofeixe", "NORMAM_Multifeixe", "Escala", "Manual", "Side Scan (Cobertura 100%)", "Side Scan (Cobertura 200%)", "Side Scan (Cobertura > 200%)"]
        ttk.Combobox(coluna_central, textvariable=self.variaveis['metodo'], values=opcoes_metodo, state="readonly").pack(fill='x', padx=5, pady=2)
        
        self.adicionar_campo(coluna_central, "Profundidade média h (m):", self.variaveis['h_media'], 'h_media')
        self.adicionar_campo(coluna_central, "Abertura angular theta (°):", self.variaveis['theta'], 'theta')
        self.adicionar_campo(coluna_central, "Cobertura MBES C_MB (%):", self.variaveis['c_mb'], 'c_mb')
        self.adicionar_campo(coluna_central, "Denominador da Escala (E):", self.variaveis['escala'], 'escala')
        self.adicionar_campo(coluna_central, "Espaçamento Manual LS (m):", self.variaveis['delta_manual'], 'delta_manual')
        self.adicionar_campo(coluna_central, "Range SSS R (m):", self.variaveis['r_sss'], 'r_sss')
        self.adicionar_campo(coluna_central, "Altitude relativa SSS alpha (%):", self.variaveis['alpha_sss'], 'alpha_sss')
        self.adicionar_campo(coluna_central, "Multiplicador de Verificação (m LV):", self.variaveis['m_lv'], 'm_lv')

        tk.Button(coluna_central, text="Executar Cálculos e Gerar Linhas", command=self.processar_calculos, bg="#0a4f94", fg="white", font=('Segoe UI', 10, 'bold')).pack(pady=25, fill='x', padx=5)

        # Coluna Direita (Visualização e Saídas)
        self.frame_mapa = tk.Frame(coluna_direita, bg="#ffffff")
        self.frame_mapa.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.frame_dashboard = tk.Frame(coluna_direita, bg="#f4f8fc", relief="groove", bd=2)
        self.frame_dashboard.pack(fill='x', padx=5, pady=5)
        
        self.variaveis_dash = {
            'metodo': tk.StringVar(value="-"),
            'ls': tk.StringVar(value="-"),
            'lv': tk.StringVar(value="-"),
            'seg': tk.StringVar(value="-"),
            'tempo': tk.StringVar(value="-")
        }
        
        self.criar_quadro_dashboard(self.frame_dashboard, "Método", self.variaveis_dash['metodo'], 0, 0)
        self.criar_quadro_dashboard(self.frame_dashboard, "Δ LS (m)", self.variaveis_dash['ls'], 0, 1)
        self.criar_quadro_dashboard(self.frame_dashboard, "Δ LV (m)", self.variaveis_dash['lv'], 0, 2)
        self.criar_quadro_dashboard(self.frame_dashboard, "Segmentos", self.variaveis_dash['seg'], 1, 0, columnspan=2)
        self.criar_quadro_dashboard(self.frame_dashboard, "Tempo (h)", self.variaveis_dash['tempo'], 1, 2)
        
        self.botao_exportar = tk.Button(coluna_direita, text="Exportar Pacote (PDF + GeoJSON)", state='disabled', command=self.exportar_pacote, bg="#22c55e", fg="white", font=('Segoe UI', 10, 'bold'))
        self.botao_exportar.pack(pady=10, fill='x', padx=5)

        self.atualizar_estado_campos()
        self.atualizar_estado_buffer()

    def adicionar_campo(self, conteiner, rotulo, variavel, chave):
        tk.Label(conteiner, text=rotulo, bg="#ffffff").pack(anchor='w', padx=5, pady=(4,0))
        entrada = tk.Entry(conteiner, textvariable=variavel)
        entrada.pack(fill='x', padx=5)
        self.entradas[chave] = entrada

    def atualizar_estado_buffer(self, *args):
        estado = 'normal' if self.variaveis['aplicar_buffer'].get() else 'disabled'
        self.entradas['buffer_m'].config(state=estado)

    def atualizar_estado_campos(self, *args):
        metodo = self.variaveis['metodo'].get()
        
        campos_especificos = ['h_media', 'theta', 'c_mb', 'escala', 'delta_manual', 'r_sss', 'alpha_sss']
        for campo in campos_especificos:
            self.entradas[campo].config(state='disabled')
            
        if metodo == 'NORMAM_Monofeixe':
            self.entradas['h_media'].config(state='normal')
        elif metodo == 'NORMAM_Multifeixe':
            self.entradas['h_media'].config(state='normal')
            self.entradas['theta'].config(state='normal')
            self.entradas['c_mb'].config(state='normal')
        elif metodo == 'Escala':
            self.entradas['escala'].config(state='normal')
        elif metodo == 'Manual':
            self.entradas['delta_manual'].config(state='normal')
        elif metodo in ['Side Scan (Cobertura 100%)', 'Side Scan (Cobertura 200%)']:
            self.entradas['r_sss'].config(state='normal')
        elif metodo == 'Side Scan (Cobertura > 200%)':
            self.entradas['r_sss'].config(state='normal')
            self.entradas['alpha_sss'].config(state='normal')

    def criar_quadro_dashboard(self, conteiner, titulo, variavel, linha, coluna, columnspan=1):
        quadro = tk.Frame(conteiner, bg="#ffffff", relief="solid", bd=1)
        quadro.grid(row=linha, column=coluna, columnspan=columnspan, sticky="nsew", padx=3, pady=3)
        tk.Label(quadro, text=titulo, font=('Segoe UI', 8, 'bold'), bg="#ffffff", fg="#5c7186").pack(anchor="center", pady=(2, 0))
        tk.Label(quadro, textvariable=variavel, font=('Consolas', 10, 'bold'), bg="#ffffff", fg="#0a4f94").pack(anchor="center", pady=(0, 2))
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
                    messagebox.showinfo("Êxito Operacional", f"Borda processada com CRS {self.gdf_area.crs.name}. Área calculada.")
                except Exception as erro:
                    messagebox.showerror("Erro de Geoprocessamento", str(erro))

    def carregar_eixo(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos Geográficos", "*.zip *.kml *.geojson")])
        if caminho:
            with tempfile.TemporaryDirectory() as dir_temp:
                try:
                    self.gdf_eixo = f.carregar_e_projetar(caminho, dir_temp)
                    comprimento_total = self.gdf_eixo.geometry.length.sum()
                    self.variaveis['comp_eixo_m'].set(round(comprimento_total, 2))
                    self.avaliar_geometrias_carregadas()
                    messagebox.showinfo("Êxito Operacional", f"Eixo processado com CRS {self.gdf_eixo.crs.name}. Comprimento calculado.")
                except Exception as erro:
                    messagebox.showerror("Erro de Geoprocessamento", str(erro))

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
            self.botao_exportar.config(state='normal')

        except Exception as excecao_calculo:
            messagebox.showerror("Interrupção Crítica", f"Falha na execução matemática ou espacial: {excecao_calculo}")

    def exportar_pacote(self):
        if self.pdf_gerado:
            diretorio = filedialog.askdirectory(title="Selecione a pasta para exportação do Pacote")
            if diretorio:
                # 1. Exporta o PDF
                caminho_pdf = os.path.join(diretorio, "Relatorio_Planejamento.pdf")
                with open(caminho_pdf, 'wb') as arquivo_saida:
                    arquivo_saida.write(self.pdf_gerado)
                
                # 2. Exporta Linhas de Sondagem (GeoJSON e CSV)
                if self.gdf_ls is not None and not self.gdf_ls.empty:
                    caminho_ls_json = os.path.join(diretorio, "Linhas_Sondagem.geojson")
                    caminho_ls_csv = os.path.join(diretorio, "Linhas_Sondagem.csv")
                    
                    self.gdf_ls.to_file(caminho_ls_json, driver="GeoJSON", engine="pyogrio")
                    f.exportar_geometria_csv(self.gdf_ls, caminho_ls_csv, "LS_")
                    
                # 3. Exporta Linhas de Verificação (GeoJSON e CSV)
                if self.gdf_lv is not None and not self.gdf_lv.empty:
                    caminho_lv_json = os.path.join(diretorio, "Linhas_Verificacao.geojson")
                    caminho_lv_csv = os.path.join(diretorio, "Linhas_Verificacao.csv")
                    
                    self.gdf_lv.to_file(caminho_lv_json, driver="GeoJSON", engine="pyogrio")
                    f.exportar_geometria_csv(self.gdf_lv, caminho_lv_csv, "LV_")
                    
                messagebox.showinfo(
                    "Exportação Concluída", 
                    "Pacote exportado com sucesso no diretório selecionado.\nVetores salvos em formatos GeoJSON e CSV estruturado."
                )
    def exibir_ajuda(self):
        texto = "Procedimento Operacional:\n1. Carregue os arquivos geográficos de Borda e Eixo.\n2. Defina os parâmetros de embarcação e buffer de recuo (opcional).\n3. Selecione o método de cálculo das LS.\n4. Preencha os campos correlatos ao método (os campos irrelevantes serão desabilitados).\n5. Execute o cálculo para ver o mapa e o dashboard, e em seguida exporte o pacote."
        messagebox.showinfo("Ajuda Técnica", texto)

    def exibir_sobre(self):
        messagebox.showinfo("Sobre o Sistema", "EasyPlanning - Módulo de Planejamento Hidrográfico\nIntegrado às normas NORMAM, ANA e IHO S-44.")

if __name__ == "__main__":
    raiz = tk.Tk()
    aplicacao = EasyPlanningApp(raiz)
    raiz.mainloop()