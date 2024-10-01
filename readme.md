# Freight Optimizer

Este projeto é uma aplicação que utiliza otimização linear para minimizar os custos de frete, com base em dados de pedidos, custos internos, custos terceirizados e capacidades de caminhões. Ele permite que o usuário selecione arquivos de entrada em formato CSV e gera uma solução ótima para a distribuição de pedidos.

## Estrutura do Projeto

- `implementacao_modelagem.py`: Contém a lógica de otimização linear utilizando a biblioteca PuLP.
- `gui.py`: Uma interface gráfica (GUI) construída em Tkinter que permite ao usuário anexar arquivos CSV e rodar o solucionador de forma interativa.
- `requirements.txt`: Lista das bibliotecas necessárias para rodar o projeto.

## Pré-requisitos

- Python 3.7 ou superior

## Instalação

1. Clone o repositório ou faça o download do projeto.
2. Abra um terminal na pasta do projeto e instale as dependências com o comando:

   ```bash
   pip install -r requirements.txt

## Como executar

1. Execute o módulo implementacao_modelagem.py diretamente via terminal:

   ```bash
   python implementacao_modelagem.py

2. Anexe os quatro arquivos CSV necessários:
   - Pedidos (exemplo: Mapa030723.csv)
   - Valores Internos (exemplo: valores_internos.csv)
   - Valores Terceirizada (exemplo: valores_terceirizada.csv)
   - Valores Terceirizada (exemplo: valores_terceirizada.csv)

3. Após anexar os arquivos, clique no botão "Solve" para rodar o solucionador. Os resultados serão exibidos na seção de saída do console da interface e salvos no arquivo PedidosAtualizados.xlsx.
