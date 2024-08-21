import subprocess
import os


def run_streamlit():
    script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'teste_streamlit.py')
    script_path = os.path.normpath(script_path)

    # Imprimir o caminho para depuração
    print(f"Caminho do script Streamlit: {script_path}")

    command = f"streamlit run {script_path}"
    subprocess.run(command, shell=True)


if __name__ == "__main__":
    run_streamlit()