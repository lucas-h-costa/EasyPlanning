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
- [Tratamento de Erros e Validação](#-tratamento-de-erros-e-validação)
- [Personalização e Temas](#-personalização-e-temas)
- [Notas Técnicas](#-notas-técnicas)
- [Créditos](#-créditos)

---

## 🎯 Visão Geral e Objetivos

O EasyPlanning foi desenvolvido com um conjunto abrangente de funcionalidades para resolver os principais desafios do planejamento hidrográfico pré-campo:

- Interface gráfica moderna em Tkinter com tema escuro customizado e painel de métricas em tempo real.
- Suporte a múltiplos métodos de espaçamento: ANA (UHE e PCH), NORMAM (Monofeixe e Multifeixe), escala cartográfica, manual, e sonar de varredura lateral (SSS).
- Geração automática de linhas de sondagem ortogonais e linhas de verificação paralelas com buffer interno opcional.
- Visualização geoespacial em Matplotlib com sobreposição de borda, eixo, LS e LV em tempo real.
- Exportação de pacote técnico completo: PDF formatado, GeoJSON vetorial e CSV estruturado.
- Interface dinâmica que habilita/desabilita campos conforme o método selecionado, reduzindo erros de preenchimento.
- Cálculo de esforço operacional com estimativa realista de tempo por navegação e manobra.
- Vetorização interativa: desenhe a borda e eixo diretamente sobre mapa de satélite.

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
  - **Reprojeção Automática:** Detecta e converte automaticamente coordenadas geográficas para o fuso UTM local mais adequado.

- 🗺️ **Vetorização Interativa**:
  - Aba dedicada com mapa de satélite interativo (Google Maps).
  - Desenhe a borda do polígono clicando pontos no mapa (mínimo 3 pontos).
  - Desenhe o eixo principal como uma polyline (mínimo 2 pontos).
  - Botão de limpeza para reiniciar o desenho sem perder os cálculos anteriores.
  - Exportação direta de vetores desenhados em KML ou GeoJSON.

- 🛡️ **Margem de Segurança e Buffer Interno**:
  - Opção para aplicar recuo paramétrico da borda em metros, impedindo que a embarcação projete linhas até encostas rasas ou margens perigosas.
  - Visualização do buffer aplicado no mapa em tempo real.

- 📐 **Motor Geométrico de Traçado de Linhas**:
  - **Linhas de Sondagem (LS):** Calculadas a distâncias regulares e projetadas ortogonalmente ao vetor tangente de cada trecho do eixo, interceptadas com o polígono de borda.
  - **Linhas de Verificação (LV):** Geradas paralelamente ao eixo através de curvas de deslocamento (*parallel offsets*), respeitando a curvatura natural do corpo d'água.

- ⏱️ **Cálculo de Esforço Operacional**:
  - Estimativa do tempo total de varredura (horas) considerando velocidade média (nós), tempo de manobra de cabeceira e extensão acumulada de linha.

- 📊 **Interface Gráfica e Dashboard Integrado**:
  - Construída com CustomTkinter com tema dark moderno e responsivo.
  - Três colunas principais: Métricas Espaciais, Configuração de Método e Visualização.
  - Formulário inteligente que habilita/desabilita parâmetros de acordo com o método escolhido.
  - Visualização cartográfica em tempo real via Matplotlib com proporção correta, cores temáticas e legenda.
  - Cartões de resumo com métricas imediatas (ΔLS, ΔLV, quantidade de segmentos e tempo total).
  - Menu de abas para acesso aos cálculos e à vetorização.

- 📄 **Exportação de Pacote Técnico**:
  - **Relatório PDF**: Documento profissional com cabeçalho institucional, tabela de parâmetros espaciais, dados operacionais e mapa vetorial em alta resolução.
  - **GeoJSON**: Camadas vetoriais `Linhas_Sondagem.geojson` e `Linhas_Verificacao.geojson`.
  - **CSV**: Coordenadas de início/fim de cada linha para importação em softwares de navegação (Hypack, QINSy).

- 💡 **Manual Integrado**:
  - Acesso a manual completo do usuário diretamente pela interface.
  - Conteúdo formatado com suporte a títulos, negrito e itálico.
  - Barra de rolagem para navegação fluida.

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
  - `customtkinter` – Interface gráfica moderna
  - `geopandas` – Processamento de dados geoespaciais
  - `pyogrio` – Suporte a leitura/escrita de formatos geoespaciais
  - `shapely` – Operações geométricas
  - `pyproj` – Transformações de coordenadas e reproj automática
  - `matplotlib` – Visualização de mapas e gráficos
  - `pandas` e `numpy` – Manipulação de dados
  - `reportlab` – Geração de relatórios PDF
  - `Pillow` – Processamento de imagens
  - `tkintermapview` – Visualização de mapas interativos em Tkinter

Todas as dependências estão listadas em `requirements.txt`.

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
conda install -c conda-forge geopandas pyogrio shapely pyproj matplotlib reportlab pillow customtkinter tkintermapview
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

A aplicação abrirá uma janela com aproximadamente 1300x850 pixels, tema escuro e todos os controles necessários para planejamento.

---

## 🖥️ Guia de Utilização

### Fluxo Principal (Aba "Parâmetros e Cálculos")

1. **Carregar Geometrias**:
   - Clique em **Carregar Borda** (barra superior) e selecione o arquivo com o polígono da área (`.zip` com SHP, `.kml` ou `.geojson`). 
   - O sistema calculará a área total, detectará o CRS e reprojetará automaticamente para UTM se necessário.
   - Clique em **Carregar Eixo** e selecione o arquivo com a linha de navegação/talvegue.
   - O sistema calculará a extensão total do eixo e estimará a largura transversal média da área.

2. **Configurar Parâmetros Operacionais**:
   - Defina a **Velocidade da embarcação** em nós.
   - Defina o **Tempo de transição (tg)** em minutos (tempo para manobra de cabeceira).
   - *(Opcional)* Marque **Aplicar Margem de Recuo** e defina a distância do buffer em metros.
   - O buffer aplica uma erosão matemática no interior do polígono, limitando as linhas à zona segura.

3. **Configurar o Método de Levantamento**:
   - No menu suspenso **"Método"**, escolha a metodologia desejada:
     - `ANA_UHE` – Para usinas hidrelétricas
     - `ANA_PCH` – Para pequenas centrais hidrelétricas
     - `NORMAM_Monofeixe` – Para ecobatímetros monofeixe
     - `NORMAM_Multifeixe` – Para ecobatímetros multifeixe
     - `Escala` – Baseado em escala cartográfica
     - `Manual` – Inserção direta de espaçamento
     - `Side Scan (Cobertura 100%)` – SSS com cobertura padrão
     - `Side Scan (Cobertura 200%)` – SSS com dupla cobertura
     - `Side Scan (Cobertura > 200%)` – SSS com cobertura completa
   - O aplicativo ativa **apenas** as caixas de texto relevantes para a metodologia selecionada.
   - Exemplo: Ao selecionar "NORMAM_Multifeixe", os campos "Profundidade média h", "Abertura angular θ" e "Cobertura MBES C_MB" ficarão habilitados; os demais permanecerão desabilitados.

4. **Executar e Visualizar**:
   - Clique em **Executar Cálculos e Gerar Linhas**.
   - O mapa central (lado direito) exibirá:
     - Polígono da borda em cinza translúcido
     - Linha do eixo em azul
     - Linhas de Sondagem (LS) em vermelho
     - Linhas de Verificação (LV) em verde
   - O painel analítico inferior (dashboard) exibirá:
     - **Método**: Metodologia aplicada
     - **Δ LS (m)**: Espaçamento entre linhas de sondagem
     - **Δ LV (m)**: Espaçamento entre linhas de verificação
     - **Segmentos**: Quantidade de linhas de sondagem geradas
     - **Tempo (h)**: Estimativa de tempo operacional em horas

5. **Exportar Pacote**:
   - Após executar os cálculos, o botão **Exportar Resultados** (lado direito, abaixo do mapa) ficará habilitado.
   - Clique nele e selecione o diretório de destino.
   - O software gerará os arquivos listados na seção [Produtos Gerados](#-produtos-gerados-e-exportação).

### Fluxo Secundário (Aba "Vetorizar área")

1. **Desenhar Borda**:
   - Clique em **Desenhar Borda**.
   - Clique no mapa para inserir vértices do polígono.
   - Após 3 ou mais pontos, o polígono será renderizado em tempo real.
   - Use **Limpar Mapa** para reiniciar.

2. **Desenhar Eixo**:
   - Clique em **Desenhar Eixo**.
   - Clique no mapa para inserir pontos da polyline.
   - Após 2 ou mais pontos, a linha será renderizada.

3. **Exportar Geometrias**:
   - Clique em **Salvar Borda (KML/JSON)** ou **Salvar Eixo (KML/JSON)**.
   - Escolha o formato (KML ou GeoJSON).
   - Os arquivos podem ser importados diretamente via **Carregar Borda/Eixo** na aba de cálculos.

---

## 📦 Produtos Gerados e Exportação

| Arquivo Gerado | Formato | Finalidade |
| :--- | :--- | :--- |
| `Relatorio_Planejamento.pdf` | PDF | Relatório técnico institucional formatado com SRC, tabelas de parâmetros, métricas operacionais e mapa renderizado. Pronto para documentação de projeto e arquivo. |
| `Linhas_Sondagem.geojson` | GeoJSON | Eixos das linhas de sondagem com projeção georreferenciada para importação em softwares de navegação (Hypack, QINSy) e SIG (QGIS, ArcGIS). |
| `Linhas_Sondagem.csv` | CSV | Coordenadas de início e fim de cada linha de sondagem em formato tabular (Leste, Norte). Estrutura nativa para importadores de embarcação. |
| `Linhas_Verificacao.geojson` | GeoJSON | Eixos das linhas de verificação/amarração para controle de qualidade dos dados batimétricos. |
| `Linhas_Verificacao.csv` | CSV | Coordenadas de início e fim de cada linha de verificação em formato tabular. |

> Todos os produtos são gerados simultaneamente ao clicar em **Exportar Resultados**.

---

## 🗂️ Estrutura do Repositório

```text
EasyPlanning/
├── app_tk.py                # Aplicação principal com interface gráfica Tkinter
│                            # Orquestração de UI, eventos, e chamadas de cálculo
├── functions_tk.py          # Módulo de funções
│                            # Cálculos matemáticos, geoprocessamento e geração de PDF
├── KML_coord.py             # Utilitário auxiliar para extração de coordenadas de KML
├── requirements.txt         # Relação de dependências Python (pip)
├── manual.md                # Manual completo do usuário em Markdown
├── pageIcon.jpg             # Ícone da aplicação (64x64 pixels, JPG)
├── icon.png                 # Ícone alternativo em PNG
├── README.md                # Este arquivo
└── .gitignore               # Arquivos ignorados pelo Git
```

---

## � Tratamento de Erros e Validação

O EasyPlanning implementa validação robusta em vários pontos:

- **Carregamento de Arquivos**: Detecta formato, CRS e converte automaticamente para UTM.
- **Reprojeção Automática**: Identifica o fuso UTM apropriado usando `estimate_utm_crs()`.
- **Validação de Geometrias**: Verifica se borda e eixo estão no mesmo CRS antes de gerar linhas.
- **Validação de Buffer**: Impede buffer inválido ou maior que a área.
- **Validação de Entrada**: Campos numéricos são validados antes de cálculos.
- **Mensagens de Feedback**: Caixas de diálogo informam ao usuário sobre sucesso, avisos e erros.

---

## 🎨 Personalização e Temas

- **Tema Dark**: Tema escuro padrão (tema azul) para reduzir cansaço visual.
- **Fonte**: Segoe UI (Windows), com fallback para sistema padrão.
- **Cores Temáticas**:
  - Azul primário: `#1f538d` (botões, títulos)
  - Verde (sucesso): `#22c55e` (exportação, carregamento)
  - Vermelho (aviso): `#ef4444` (limpeza, erro)
  - Cinza (fundo): `#1a1a1a`, `#1c1d1d`

---

## 📝 Notas Técnicas

- **Projeção de Saída**: Todas as linhas de sondagem e verificação são geradas em UTM (a projeção é detectada automaticamente conforme a latitude/longitude de entrada).
- **Precisão de Cálculo**: Operações geométricas utilizam `Shapely` com precisão de ponto flutuante padrão (tolerância ~1e-9).
- **Performance**: Aplicação otimizada para áreas de até ~10.000 km², com performance linear no número de linhas.
- **Compatibilidade**: Testado em Windows 10/11 com Python 3.10+. Deve funcionar em Linux e macOS com pequenos ajustes de caminho de ícone.

---

## �👥 Créditos

- **Desenvolvedor Principal:** Lucas Costa
- **Orientação e Pesquisa:**  Prof. Italo Ferreira, Grupo de Pesquisas em Hidrografia (**GPHIDRO**)
- **Instituição:** Universidade Federal de Viçosa (**UFV**) – Departamento de Engenharia Civil / Agrimensura e Cartografia
- **Contexto:** Projeto de Iniciação Científica (IC) – 2025/2026

---

## 📧 Suporte e Contato

Para dúvidas, sugestões ou relato de problemas, abra uma issue no repositório ou entre em contato através do email dacosta.lhm@gmail.com.

---

**Versão:** 1.0  
**Data de Lançamento:** Setembro de 2025  
**Licença:** A definir conforme política de código aberto da instituição.

