# Manual técnico do EasyPlanning

## 1. Finalidade e escopo

O EasyPlanning é um protótipo desenvolvido por Lucas H. Costa, sob orientação do Prof. Ítalo Ferreira (GPHIDRO/UFV). Sua finalidade é apoiar o planejamento preliminar de levantamentos hidrográficos por meio de:

- leitura de geometrias de área e eixo em formatos vetoriais;
- conversão para um sistema de coordenadas adequado a cálculos métricos;
- estimativa de espaçamentos para linhas de sondagem (LS) e linhas de verificação (LV);
- geração de linhas por operações geométricas de interseção e deslocamento;
- estimativa simplificada do tempo de operação;
- produção de visualização cartográfica, arquivos vetoriais, CSV e relatório PDF.

Os resultados são auxiliares ao planejamento. Eles não substituem a especificação técnica, a seleção de sensores, a análise das condições locais, a verificação de campo ou a avaliação de um profissional habilitado.

## 2. Organização da interface

### 2.1 Aba "Parâmetros e Cálculos"

A aba principal está organizada em três áreas:

1. **Métricas espaciais:** área total, comprimento do eixo, velocidade, tempo de transição e parâmetros de recuo.
2. **Configuração do método:** método de espaçamento e parâmetros específicos.
3. **Visualização e saídas:** planta cartográfica, painel de métricas e botão de exportação.

Os botões **Carregar Borda** e **Carregar Eixo** ficam na barra superior. O botão **Executar Cálculos e Gerar Linhas** só deve ser utilizado depois que as duas geometrias forem carregadas.

### 2.2 Aba "Vetorizar área"

Esta aba permite criar geometrias diretamente sobre o mapa:

- **Desenhar Borda:** inicia a coleta de vértices do polígono da área. São necessários pelo menos três pontos.
- **Desenhar Eixo:** inicia a coleta de pontos da linha de referência. São necessários pelo menos dois pontos.
- **Limpar Mapa:** remove pontos, marcadores, polígonos e linhas desenhados.
- **Salvar Borda (KML/JSON):** exporta o polígono em KML ou GeoJSON.
- **Salvar Eixo (KML/JSON):** exporta a linha em KML ou GeoJSON.

As coordenadas coletadas pelo mapa são inicialmente geográficas, em latitude e longitude. Os arquivos exportados recebem o CRS `EPSG:4326` e são reprojetados quando carregados na aba de cálculos.

## 3. Entrada de dados espaciais

### 3.1 Formatos aceitos

Para a borda e para o eixo, o carregador aceita:

- `.kml`;
- `.geojson`;
- `.zip` contendo pelo menos um arquivo `.shp` e seus arquivos auxiliares.

No caso de ZIP, o primeiro Shapefile encontrado é utilizado. O conjunto deve conter os arquivos auxiliares associados ao Shapefile e geometrias compatíveis com a função escolhida: uma área poligonal para a borda e uma geometria linear para o eixo. Quando houver mais de uma feição, as geometrias são consideradas conjuntamente no processamento espacial.

### 3.2 Sistema de coordenadas e unidades

O aplicativo lê o sistema de referência informado no arquivo. Se o CRS estiver ausente ou for geográfico, o programa estima uma projeção UTM e reprojeta a camada. A área, o comprimento, os recuos e os espaçamentos são calculados nas unidades da projeção, normalmente metros. Essa etapa é necessária porque cálculos de distância e área diretamente em latitude e longitude não são apropriados para a finalidade do planejamento.

Depois que as duas camadas são carregadas, o eixo é convertido para o sistema de coordenadas da borda quando necessário. Antes de executar os cálculos, deve-se conferir se:

- a borda é válida e representa a área de interesse;
- o eixo está contido ou cruza a borda;
- as geometrias possuem escala e localização corretas;
- o CRS utilizado é apropriado para medições locais;
- a área e o comprimento apresentados são compatíveis com as dimensões conhecidas do local.

## 4. Parâmetros de entrada

| Campo | Unidade | Uso |
| :--- | :--- | :--- |
| Área Total | m² | Área usada nos métodos ANA. É preenchida ao carregar a borda. |
| Comprimento do Eixo | m | Comprimento usado nos métodos ANA e na estimativa de linhas. É preenchido ao carregar o eixo. |
| Velocidade da embarcação | nós | Velocidade constante usada na conversão para distância por hora. |
| Tempo de transição `tg` | min | Tempo de manobra entre linhas consecutivas. |
| Distância do recuo | m | Valor do buffer interno aplicado à borda, quando habilitado. |
| Profundidade média `h` | m | Parâmetro dos métodos NORMAM monofeixe e multifeixe. |
| Abertura angular `theta` | graus | Abertura do feixe no método NORMAM multifeixe. |
| Cobertura `C_MB` | % | Percentual usado no cálculo multifeixe. |
| Denominador da escala `E` | adimensional | Parâmetro do método baseado em escala cartográfica. |
| Espaçamento manual | m | Valor de `ΔLS` no método Manual. |
| Range SSS `R_sss` | m | Alcance lateral no método Side Scan Sonar. |
| Altitude relativa `alpha` | % | Compensação usada na cobertura SSS superior a 200%. |
| Multiplicador `m_LV` | adimensional | Relação entre o espaçamento de LV e o espaçamento de LS. |

Ao selecionar um método, a interface habilita somente os campos específicos necessários. Os campos gerais permanecem disponíveis para todos os métodos.

## 5. Métodos de cálculo

O programa calcula primeiro `ΔLS` e, em seguida, calcula `ΔLV` por meio de:

$$\Delta LV = m_{LV} \cdot \Delta LS$$

### 5.1 ANA UHE e ANA PCH

A área é convertida de metros quadrados para hectares e o comprimento do eixo de metros para quilômetros.

Para UHE:

$$\Delta LS = \left(\frac{0{,}35 \cdot A_{ha}^{0{,}35}}{L_{km}}\right) \cdot 1000$$

Para PCH:

$$\Delta LS = \left(\frac{0{,}10 \cdot A_{ha}^{0{,}25}}{L_{km}}\right) \cdot 1000$$

Se o comprimento do eixo for zero, o programa retorna `ΔLS = 0` e `ΔLV = 0`.

### 5.2 NORMAM monofeixe

O espaçamento é obtido pela profundidade média:

$$\Delta LS = \lceil\max(3h, 25)\rceil$$

### 5.3 NORMAM multifeixe

Primeiro calcula-se a largura da faixa acústica:

$$W = 2h\tan\left(\frac{\theta}{2}\right)$$

Depois:

$$\Delta LS = \left\lceil1{,}5W - W\left(\frac{C_{MB}}{200}\right)\right\rceil$$

### 5.4 Escala e método manual

No método de escala, o espaçamento é:

$$\Delta LS = 0{,}005E$$

No método manual, o valor informado pelo usuário é utilizado diretamente.

### 5.5 Side Scan Sonar

Para `R_sss` como alcance lateral:

- cobertura de 100%: `ΔLS = 2R_sss`;
- cobertura de 200%: `ΔLS = R_sss`;
- cobertura superior a 200%: `ΔLS = R_sss(1 - alpha/100)`.

## 6. Geração das linhas

Quando o recuo está habilitado, o programa aplica uma erosão interna ao polígono da área por meio de um buffer negativo com a distância informada. Se a área resultante for vazia, o processamento é interrompido. Todas as interseções das linhas planejadas são calculadas contra essa área de recorte, e não contra o polígono original.

### 6.1 Linhas de sondagem

O eixo é percorrido a intervalos regulares de `ΔLS`, iniciando na distância zero. Em cada posição, o programa:

1. interpola o ponto correspondente no eixo;
2. utiliza pontos próximos para estimar o vetor tangente local;
3. rotaciona esse vetor em 90 graus para obter a direção perpendicular;
4. cria uma linha perpendicular de extensão ampla;
5. calcula a interseção dessa linha com a área de recorte;
6. inclui as interseções não vazias como linhas de sondagem.

Quando nenhuma interseção é encontrada, nenhuma linha de sondagem é produzida.

### 6.2 Linhas de verificação

O eixo central é primeiro recortado pela área. Em seguida, são geradas linhas paralelas em ambos os lados do eixo, nos afastamentos `ΔLV`, `2ΔLV`, `3ΔLV` e assim por diante. O processo termina quando nenhum dos dois deslocamentos produz nova interseção com a área.

Dependendo da geometria de entrada, uma linha pode resultar em um ou mais segmentos. Isso ocorre, por exemplo, quando uma interseção atravessa partes desconectadas ou quando a borda possui configuração geométrica complexa.

## 7. Estimativa do tempo operacional

A aplicação utiliza a seguinte expressão:

$$T = \frac{L_{total}}{v_{nos}\cdot1852} + \left(\frac{t_g}{60}\cdot\max(0,n_s-1)\right)$$

Para a estimativa, a quantidade de linhas é obtida a partir do comprimento do eixo e de `ΔLS`, considerando pelo menos uma linha quando o espaçamento é positivo.

O fator `1852` relaciona nós e distância. A estimativa não inclui deslocamentos até a área, condições de maré e corrente, mudanças de velocidade, falhas de aquisição ou outras pausas operacionais.

## 8. Outputs e interpretação

Após o processamento, o dashboard apresenta:

| Output | Interpretação |
| :--- | :--- |
| Método | Critério selecionado para o cálculo. |
| `ΔLS (m)` | Espaçamento calculado entre posições das linhas de sondagem. |
| `ΔLV (m)` | Espaçamento calculado entre linhas de verificação. |
| Segmentos | Quantidade estimada de linhas de sondagem usada no dashboard e no tempo. |
| Tempo (h) | Estimativa do tempo de navegação e manobras. |

A planta apresenta a área, o recuo quando aplicado, o eixo, as LS e as LV. A representação deve ser utilizada como controle visual: linhas ausentes, segmentos inesperados ou geometrias fragmentadas indicam a necessidade de revisar os dados de entrada.

## 9. Exportação

O botão **Exportar Resultados** grava os produtos no diretório escolhido:

| Arquivo | Conteúdo |
| :--- | :--- |
| `Relatorio_Planejamento.pdf` | CRS, área, comprimento, buffer, método, parâmetros operacionais, espaçamentos, quantidade estimada, tempo e planta. |
| `Linhas_Sondagem.geojson` | Geometrias das interseções das linhas de sondagem com a área de recorte. |
| `Linhas_Sondagem.csv` | Nome, coordenadas métricas de início e fim de cada `LineString` ou parte de `MultiLineString`. |
| `Linhas_Verificacao.geojson` | Geometrias das linhas de verificação intersectadas com a área. |
| `Linhas_Verificacao.csv` | Nome, coordenadas métricas de início e fim de cada segmento de verificação. |

O CSV utiliza o cabeçalho:

```text
nome da linha,E inicio,N inicio,E fim,N fim
```

As coordenadas são gravadas com três casas decimais. O arquivo não contém todos os vértices das linhas, atributos de profundidade ou informações de navegação; ele registra apenas os extremos dos segmentos para cada geometria exportada.

## 10. Relatório PDF

O relatório PDF é gerado ao final do processamento e contém:

1. dados espaciais, incluindo CRS, área, comprimento e buffer;
2. método, velocidade, espaçamentos e quantidade estimada de segmentos;
3. parâmetros adicionais quando aplicáveis, como profundidade, abertura angular, cobertura, escala, range e altitude relativa;
4. imagem da planta cartográfica.

O arquivo serve como registro dos parâmetros utilizados em uma execução. Para garantir rastreabilidade, recomenda-se conservar o relatório junto aos arquivos de entrada correspondentes.

## 11. Problemas frequentes

- **Nenhum Shapefile encontrado:** confirme que o ZIP contém um `.shp` e seus arquivos auxiliares.
- **Área ou comprimento incompatível:** verifique o CRS e a unidade das geometrias antes do carregamento.
- **Área vazia após o buffer:** reduza a distância do recuo ou revise o polígono de entrada.
- **Nenhuma linha gerada:** confira se o eixo cruza a área e se os espaçamentos são positivos.
- **Erro ao exportar:** confirme se o diretório selecionado permite a gravação dos arquivos.

