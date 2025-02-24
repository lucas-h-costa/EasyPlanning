import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import geopandas as gpd
import functions as f
# Importa a função principal

# Função para abrir um diálogo de arquivo e retornar o caminho
def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_label.config(text=f"Arquivo selecionado: {file_path}")
    return file_path

# Função para realizar os cálculos e exibir o resultado
def calculate_operation():
      # Chama a função de cálculo
    output_textbox.delete("1.0", "end")
    output_textbox.insert("1.0", f"O cálculo foi concluído: {result}")
    messagebox.showinfo("Resultado", f"O cálculo foi concluído!")

# Função para salvar o resultado em CSV
def save_csv(data):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        data.to_csv(file_path, index=False)
        messagebox.showinfo("Salvar Arquivo", f"Arquivo salvo com sucesso em {file_path}")

# Função para gerar os dados e oferecer a opção de salvar em CSV
def generate_and_save():
    result = some_function()  # Gera os dados
    data = pd.DataFrame({
        "Coluna1": [1, 2, 3],
        "Coluna2": [4, 5, 6]
    })
    output_textbox.delete("1.0", "end")
    output_textbox.insert("1.0", f"Dados gerados:\n{data}")
    
    # Pergunta se o usuário quer salvar os resultados em CSV
    save_prompt = messagebox.askyesno("Salvar CSV", "Deseja salvar os resultados em um arquivo CSV?")
    if save_prompt:
        save_csv(data)

# Função principal que cria a interface Tkinter
def main():
    root = tk.Tk()
    root.title("Easy Planner")
    root.geometry("800x600")  # Define o tamanho da janela

    # Botão para abrir arquivo
    open_button = tk.Button(root, text="Abrir Arquivo", command=open_file)
    open_button.pack(pady=10)

    # Label para mostrar o arquivo selecionado
    global file_label
    file_label = tk.Label(root, text="Nenhum arquivo selecionado")
    file_label.pack()

    tk.Entry()
    # Botão para executar o cálculo
    calc_button = tk.Button(root, text="Calcular", command=calculate_operation)
    calc_button.pack(pady=10)

    # Caixa de texto para mostrar o resultado
    global output_textbox
    output_textbox = tk.Text(root, height=10, width=50)
    output_textbox.pack(pady=10)

    # Botão para salvar como CSV
    save_button = tk.Button(root, text="Salvar como CSV", command=generate_and_save)
    save_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()

