from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus
import pandas as pd

def run_solver(pedidos_path, valores_internos_path, valores_terceirizada_path, caminhoes_path, output_func=print):
    # Carregando os dados do problema
    pedidos_df = pd.read_csv(pedidos_path, sep=';', decimal=',')
    valores_internos_df = pd.read_csv(valores_internos_path, sep=';', decimal=',')
    valores_terceirizada_df = pd.read_csv(valores_terceirizada_path, sep=';', decimal=',')
    caminhoes_df = pd.read_csv(caminhoes_path, sep=';', decimal=',')

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

    def get_external_cost(region, weight, cost_data, alpha=1.2):
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

    # Imprimir o valor da função objetivo
    output_func(f"Custo total de frete: R${model.objective.value():.2f} \n")

    # Verificar se a capacidade dos caminhões foi respeitada após a solução
    for i in range(len(caminhoes)):
        carga_total = sum(z_vars[i, j].varValue * pedidos[j][2] for j in range(len(pedidos)))
        output_func(f'Caminhão {caminhoes[i][0]} (Capacidade: {caminhoes[i][1]} kg) - Carga total alocada: {carga_total:.2f} kg \n')
        print(f'Caminhão {caminhoes[i][0]} (Capacidade: {caminhoes[i][1]} kg) - Carga total alocada: {carga_total} kg')
        
        # Debugging: Verificar cada pedido
        for j in range(len(pedidos)):
            print(f'  Pedido {pedidos[j][0]}: {z_vars[i, j].varValue} (Peso: {pedidos[j][2]} kg)')
        
        if carga_total > caminhoes[i][1]:
            print(f"Atenção: A capacidade do caminhão {caminhoes[i][0]} foi excedida!")

    # Adicionar as novas colunas ao DataFrame de pedidos
    pedidos_df['Modalidade Frete'] = ''
    pedidos_df['Caminhao'] = ''

    # Checar se a solução é ótima
    if LpStatus[model.status] == 'Optimal':
        # Atualizar as colunas com base nos resultados do modelo
        for j in range(len(pedidos)):
            for i in range(len(caminhoes)):
                if z_vars[i, j].varValue > 0:
                    pedidos_df.loc[j, 'Modalidade Frete'] = 'Interno'
                    pedidos_df.loc[j, 'Caminhao'] = caminhoes[i][0]
                    break
            if y_vars[j].varValue > 0:
                pedidos_df.loc[j, 'Modalidade Frete'] = 'Externo'
                pedidos_df.loc[j, 'Caminhao'] = ''

        # Salvar o DataFrame atualizado em um novo arquivo CSV
        pedidos_df.to_csv('Mapa030723_atualizado.csv', sep=';', decimal=',', index=False)
        return "Resultados extraídos e salvos com sucesso em 'Mapa030723_atualizado.csv'."
    else:
        return "Não foi encontrada uma solução ótima para o problema."