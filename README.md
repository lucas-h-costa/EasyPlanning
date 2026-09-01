# 🗺️ EasyPlanning - Módulo de Planejamento Hidrográfico

O **EasyPlanning** é uma aplicação desktop desenvolvida em Python para automatizar, otimizar e padronizar o planejamento pré-campo de levantamentos batimétricos e hidrográficos. Criado no âmbito do **GPHIDRO** (Grupo de Pesquisas em Hidrografia) da **Universidade Federal de Viçosa (UFV)** como projeto de Iniciação Científica (IC), o software integra normas técnicas nacionais e internacionais (ANA, NORMAM/DHN, IHO S-44) com algoritmos de geoprocessamento para traçado automatizado de linhas de sondagem (LS) e verificação (LV), cálculo de esforço operacional e geração de relatórios técnicos completos em PDF.

---

## 📌 Sumário

- [Visão Geral e Objetivos](#-visão-geral-e-objetivos)
- [Principais Funcionalidades](#-principais-funcionalidades)
- [Métodos de Cálculo e Critérios Normativos](#-métodos-de-cálculo-e-critérios-normativos)
- [Requisitos e Dependências](#-requisitos-e-dependências)
- [Instalação e Execução](#-instalação-e-execução)
- [Guia de Utilização](#-guia-de-utilização)
- [Produtos Gerados e Exportação](#-produtos-gerados-e-exportação)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Créditos](#-créditos)

---

## 🎯 Visão Geral e Objetivos

O planejamento prévio de uma campanha hidrográfica é uma das etapas mais críticas para assegurar a qualidade dos dados, a segurança da navegação da embarcação e a viabilidade econômica do levantamento. 

O **EasyPlanning** resolve as principais dores do planejamento manual:
1. **Eliminação de cálculos manuais repetitivos** para dimensionamento do espaçamento de linhas.
2. **Geração geométrica precisa** de linhas de sondagem transversais ortogonais ao talvegue/eixo e linhas de verificação longitudinais paralelas.
3. **Estimativa realista do tempo de levantamento**, considerando a velocidade da embarcação e o tempo despendido em manobras de giro entre linhas.
4. **Exportação imediata para softwares de navegação e SIG** (Hypack, PDS2000, QINSy, QGIS, ArcGIS).
5. **Geração de documentação padronizada** por meio de relatório técnico para aprovação em órgãos fiscalizadores e contratações de engenharia.

---

## 🚀 Principais Funcionalidades

- 📁 **Ingestão Multi-formato de Dados Espaciais**:
  - Aceita a delimitação da área (**Borda**) e o traçado central (**Eixo de Navegação/Talvegue**).
  - Suporta pacotes Shapefile em arquivo compactado (`.zip` contendo `.shp`, `.shx`, `.dbf`, `.prj`), arquivos do Google Earth (`.kml`) e `.geojson`.
  - **Reprojeção Automática:** Detecta e converte automaticamente coordenadas geográficas para o fuso UTM local mais adequado (`estimate_utm_crs()`).
- 🛡️ **Margem de Segurança e Buffer Interno**:
  - Opção para aplicar recuo paramétrico da borda em metros, impedindo que a embarcação projete linhas até encostas rasas ou margens perigosas.
- 📐 **Motor Geométrico de Traçado de Linhas**:
  - **Linhas de Sondagem (LS):** Calculadas a distâncias regulares e projetadas ortogonalmente ao vetor tangente de cada trecho do eixo, interceptadas com o polígono de borda.
  - **Linhas de Verificação (LV):** Geradas paralelamente ao eixo através de curvas de deslocamento (*parallel offsets*), respeitando a curvatura natural do corpo d'água.
- ⏱️ **Cálculo de Esforço Operacional**:
  - Estimativa do tempo total de varredura (horas) considerando velocidade média (nós), tempo de manobra de cabeceira ($t_g$) e extensão acumulada de linha.
- 📊 **Interface Gráfica e Dashboard Integrado**:
  - Construída com Tkinter, interface responsiva e formulário inteligente (habilita/desabilita parâmetros de acordo com o método escolhido).
  - Visualização cartográfica em tempo real via Matplotlib com proporção correta (`aspect='equal'`), cores temáticas e legenda.
  - Cartões de resumo com métricas imediatas ($\Delta LS$, $\Delta LV$, quantidade de segmentos e tempo total).
- 📄 **Exportação de Pacote Técnico**:
  - **Relatório PDF**: Documento profissional com cabeçalho institucional, tabela de parâmetros espaciais, dados operacionais e mapa vetorial em alta resolução.
  - **GeoJSON**: Camadas vetoriais `Linhas_Sondagem.geojson` e `Linhas_Verificacao.geojson`.

---

## 📐 Métodos de Cálculo e Critérios Normativos

O EasyPlanning contempla os principais critérios regulatórios e empíricos aplicados na engenharia hidrográfica:

### 1. Diretrizes da ANA (Agência Nacional de Águas e Saneamento Básico)
* **ANA UHE (Usinas Hidrelétricas):**
  $$\Delta LS = \left( \frac{0{,}35 \cdot A_{ha}^{0{,}35}}{L_{km}} \right) \times 1000$$
* **ANA PCH (Pequenas Centrais Hidrelétricas):**
  $$\Delta LS = \left( \frac{0{,}10 \cdot A_{ha}^{0{,}25}}{L_{km}} \right) \times 1000$$
  *Onde $A_{ha}$ é a área do reservatório em hectares e $L_{km}$ é o comprimento do eixo em quilômetros.*

### 2. Normas da Autoridade Marítima (NORMAM - DHN / Marinha do Brasil)
* **NORMAM Monofeixe (Single-Beam Echo Sounder - SBES):**
  Espaçamento em função da profundidade média local ($h$):
  $$\Delta LS = \max(3 \cdot h, 25{,}0 \text{ m})$$
* **NORMAM Multifeixe (Multibeam Echo Sounder - MBES):**
  Calcula a largura da faixa acústica (*swath*) $W$ para abertura angular $\theta$ e aplica a porcentagem de sobreposição requerida ($C_{MB}$):
  $$W = 2 \cdot h \cdot \tan\left(\frac{\theta}{2}\right)$$
  $$\Delta LS = \left\lceil 1{,}5 \cdot W - W \cdot \left(\frac{C_{MB}}{200}\right) \right\rceil$$

### 3. Escala Cartográfica (Critério Gráfico / IHO)
Baseado no erro gráfico admissível no papel (5 mm na escala da carta):
$$\Delta LS = 0{,}005 \cdot E = \frac{E}{200}$$
*Exemplo: Para escala $1:2.000$, $\Delta LS = 10\text{ m}$.*

### 4. Sonar de Varredura Lateral (Side Scan Sonar - SSS)
Dimensionado a partir do alcance lateral do sonar ($R_{sss}$) e da taxa de cobertura:
* **Cobertura 100%:** $\Delta LS = 2 \cdot R_{sss}$
* **Cobertura 200%:** $\Delta LS = R_{sss}$
* **Cobertura > 200% (Varredura com compensação de nadir $\alpha$):**
  $$\Delta LS = R_{sss} \cdot \left(1 - \frac{\alpha}{100}\right)$$

### 5. Linhas de Verificação (LV)
As linhas de controle/verificação cruzam as linhas de sondagem para garantir a consistência vertical do levantamento:
$$\Delta LV = m_{LV} \cdot \Delta LS$$
*(O multiplicador $m_{LV}$ padrão recomendado por normas costuma ser 10).*

### 6. Estimativa de Tempo de Operação
$$\text{Tempo (h)} = \frac{L_{total}}{v_{nos} \cdot 1852} + \left(\frac{t_g}{60} \cdot \max(0, n_s - 1)\right)$$
*Onde $L_{total}$ é o comprimento somado de todas as linhas de sondagem projetadas, $v_{nos}$ é a velocidade de navegação, $t_g$ é o tempo de manobra por cabeceira em minutos e $n_s$ é a quantidade total de linhas.*

---

## 🛠️ Requisitos e Dependências

- **Python:** 3.10 ou superior
- Bibliotecas necessárias:
  - `geopandas`
  - `pyogrio`
  - `shapely`
  - `pyproj`
  - `matplotlib`
  - `pandas` e `numpy`
  - `reportlab`
  - `Pillow`
  - `rarfile`

---

## 📥 Instalação e Execução

### Opção 1: Utilizando ambiente Conda (Recomendado para GIS)

O Conda facilita a instalação de pacotes geoespaciais e dependências C (GDAL, GEOS, PROJ):

```bash
# Clone ou baixe o repositório
git clone https://github.com/lucas-h-costa/EasyPlanning.git
cd EasyPlanning

# Crie e ative um ambiente
conda create -n easyplanning python=3.11 -y
conda activate easyplanning

# Instale as dependências
conda install -c conda-forge geopandas pyogrio shapely pyproj matplotlib reportlab pillow
```

### Opção 2: Utilizando `pip` e ambiente virtual

```bash
# Clone ou baixe o repositório
cd EasyPlanning

# Crie e ative um ambiente virtual
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate

# Instale os requisitos
pip install -r requirements.txt
```

### 🚀 Executando a Aplicação

Para iniciar o programa com interface gráfica:

```bash
python app_tk.py
```

---

## 🖥️ Guia de Utilização

1. **Carregar Geometrias**:
   - Clique em **Carregar Borda** e selecione o arquivo com o polígono da área (`.zip` com SHP, `.kml` ou `.geojson`). O sistema calculará a área total e o CRS projetado.
   - Clique em **Carregar Eixo** e selecione o arquivo com a linha de navegação/talvegue. O sistema calculará a extensão e estimará a largura transversal média.
2. **Definir Parâmetros Operacionais**:
   - Ajuste a velocidade da embarcação em nós e o tempo estimado de manobra por cabeceira.
   - *(Opcional)* Marque **Aplicar Buffer Interno** e defina a distância de recuo das margens em metros.
3. **Configurar o Método de Levantamento**:
   - No menu seletor, escolha a metodologia desejada (ANA, NORMAM, Escala, Manual ou Side Scan).
   - O aplicativo ativará exclusivamente as caixas de texto relevantes para a metodologia selecionada (ex: profundidade média, ângulo do feixe, alcance, escala).
4. **Executar e Visualizar**:
   - Clique em **Executar Cálculos e Gerar Linhas**.
   - O mapa central exibirá a área, a borda recuada, o eixo, as Linhas de Sondagem (vermelho) e as Linhas de Verificação (verde).
   - O dashboard inferior atualizará os indicadores operacionais.
5. **Exportar**:
   - Clique no botão verde **Exportar Pacote (PDF + GeoJSON)**.
   - Selecione o diretório de destino. O software gerará:
     - `Relatorio_Planejamento.pdf`
     - `Linhas_Sondagem.geojson`
     - `Linhas_Verificacao.geojson`

---

## 📦 Produtos Gerados e Exportação

| Arquivo Gerado | Formato | Finalidade |
| :--- | :--- | :--- |
| `Relatorio_Planejamento.pdf` | Documento PDF | Relatório técnico institucional formatado, pronto para documentação e arquivo de projeto. |
| `Linhas_Sondagem.geojson` | Vetorial GeoJSON | Eixos das linhas de sondagem com projeção georreferenciada para importação em softwares de navegação e SIG. |
| `Linhas_Verificacao.geojson` | Vetorial GeoJSON | Eixos das linhas de amarração e verificação para controle de qualidade dos dados. |

---

## 🗂️ Estrutura do Repositório

```text
EasyPlanning/
├── app_tk.py           # Aplicação principal com interface gráfica Tkinter e orquestração
├── functions_tk.py     # Módulo de cálculos matemáticos, geoprocessamento e geração de PDF
├── KML_coord.py        # Utilitário para extração de coordenadas e vértices de arquivos KML
├── requirements.txt    # Relação de dependências do Python
├── pageIcon.jpg        # Ícone da janela e identidade visual da aplicação
├── icon.png            # Ícone alternativo em formato PNG
└── README.md           # Documentação completa do projeto
```

---

## 👥 Créditos

- **Desenvolvedor:** Lucas Costa
- **Orientação e Pesquisa:** Grupo de Pesquisas em Hidrografia (**GPHIDRO**)
- **Instituição:** Universidade Federal de Viçosa (**UFV**) - Departamento de Engenharia Civil / Agrimensura e Cartografia
- **Contexto:** Projeto de Iniciação Científica (IC)

