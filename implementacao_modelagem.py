from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus
import pandas as pd

# Carregando os dados do problema
pedidos_df = pd.read_csv('Mapa030723.csv', sep=';', decimal=',')
valores_internos_df = pd.read_csv('valores_internos.csv', sep=';', decimal=',')
valores_terceirizada_df = pd.read_csv('valores_terceirizada.csv', sep=';', decimal=',')
caminhoes_df = pd.read_csv('base_de_caminhoes.csv', sep=';', decimal=',')

# Criando o modelo de otimização
model = LpProblem(name="minimize_frete", sense=LpMinimize)

# Carregar os dados dos pedidos, caminhões e multiplicadores em variáveis
pedidos = pedidos_df[['Numero do Pedido', 'Regiao', 'Peso Pedido']].values
caminhoes = caminhoes_df[['Identificacao', 'Peso Maximo']].values
valores_internos = valores_internos_df.set_index('Regiao').fillna(0).to_dict()
valores_terceirizada = valores_terceirizada_df.set_index('Regiao').fillna(0).to_dict()

# Definindo variáveis de decisão z_ij e y_j
z_vars = LpVariable.dicts("z", [(i, j) for i in range(len(caminhoes)) for j in range(len(pedidos))], cat='Binary')
y_vars = LpVariable.dicts("y", [j for j in range(len(pedidos))], cat='Binary')

# Funções auxiliares para calcular os custos de frete interno e terceirizado
def get_internal_cost(region, weight, cost_data):
    weight_ranges = ["ate 500kg", "de 501kg a 1000kg", "de 1001kg a 5000kg", "de 5001kg a 15000kg", "de 15001 a 20000kg"]
    for i, (lower, upper) in enumerate([(0, 500), (501, 1000), (1001, 5000), (5001, 15000), (15001, 20000)]):
        if lower < weight <= upper:
            cost = cost_data[weight_ranges[i]][region]
            if isinstance(cost, str):
                cost = float(cost.replace(',', '.'))
            return cost * weight
    return 0

def get_external_cost(region, weight, cost_data, alpha=1.2):  # Exemplo de α = 1.2
    weight_ranges = ["ate 500kg", "de 501kg a 1000kg", "de 1001kg a 5000kg", "de 5001kg a 15000kg", "de 15001 a 20000kg"]
    for i, (lower, upper) in enumerate([(0, 500), (501, 1000), (1001, 5000), (5001, 15000), (15001, 20000)]):
        if lower < weight <= upper:
            cost = cost_data[weight_ranges[i]][region]
            if isinstance(cost, str):
                cost = float(cost.replace(',', '.'))
            return alpha * cost * weight
    return 0

# Definindo a função objetivo (minimizar o custo total de frete)
model += lpSum([
    z_vars[i, j] * get_internal_cost(pedidos[j][1], pedidos[j][2], valores_internos) 
    for i in range(len(caminhoes)) for j in range(len(pedidos))
]) + lpSum([
    y_vars[j] * get_external_cost(pedidos[j][1], pedidos[j][2], valores_terceirizada)
    for j in range(len(pedidos))
])

# Restrições de capacidade dos caminhões internos
for i in range(len(caminhoes)):
    model += lpSum(z_vars[i, j] * pedidos[j][2] for j in range(len(pedidos))) <= caminhoes[i][1], f"Capacidade_Caminhao_{i}"

# Restrições de satisfação da demanda dos pedidos
for j in range(len(pedidos)):
    model += lpSum(z_vars[i, j] for i in range(len(caminhoes))) + y_vars[j] == 1

# Resolver o modelo
model.solve()

# Verificar os resultados
for v in model.variables():
    if v.varValue > 0:
        print(f'{v.name}: {v.varValue}')

# Verificar se a capacidade dos caminhões foi respeitada após a solução
for i in range(len(caminhoes)):
    carga_total = sum(z_vars[i, j].varValue * pedidos[j][2] for j in range(len(pedidos)))
    print(f'Caminhão {caminhoes[i][0]} (Capacidade: {caminhoes[i][1]} kg) - Carga total alocada: {carga_total} kg')
    if carga_total > caminhoes[i][1]:
        print(f"Atenção: A capacidade do caminhão {caminhoes[i][0]} foi excedida!")

# Checar se a solução é ótima
if LpStatus[model.status] == 'Optimal':
    # Inicializar as colunas na planilha
    pedidos_df['Modalidade do Frete'] = 'Externo'  # Definir padrão como 'Externo'
    pedidos_df['Caminhão'] = None  # Inicializar com None

    # Atualizar os resultados de z_vars (caminhão e pedido) e y_vars (modalidade de frete)
    for j in range(len(pedidos)):
        pedido_id = pedidos[j][0]  # Obtemos o número do pedido atual

        # Verificar a variável y_vars[j] para definir a modalidade de frete
        if y_vars[j].varValue == 0:  # Se y_var é 0, o frete é interno
            pedidos_df.loc[pedidos_df['Numero do Pedido'] == pedido_id, 'Modalidade do Frete'] = 'Interno'
            
            # Encontrar qual caminhão foi selecionado para esse pedido
            for i in range(len(caminhoes)):
                if z_vars[i, j].varValue == 1:
                    pedidos_df.loc[pedidos_df['Numero do Pedido'] == pedido_id, 'Caminhão'] = caminhoes[i][0]
                    break

    # Salvar os resultados em um arquivo XLSX
    pedidos_df.to_excel("PedidosAtualizados.xlsx", index=False)
    print("Resultados extraídos e salvos com sucesso em 'PedidosAtualizados.xlsx'.")
else:
    print("Não foi encontrada uma solução ótima para o problema.")