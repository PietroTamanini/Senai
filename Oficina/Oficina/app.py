import json
import datetime
import os

# ======================= CONSTANTES =======================
ARQUIVO_DADOS = "dados.json"

# ======================= VARIÁVEIS GLOBAIS =======================
pecas = []
servicos = []
clientes = []
veiculos = []
pedido_atual = []
vendas = []
somaPontos = 0 # Pontos acumulados do usuário logado

# Usuários pré-cadastrados
usuarios = [
    {"usuario": "ademiro", "senha": "999", "nivel": "admin"},
    {"usuario": "cara", "senha": "111", "nivel": "atendente"},
    {"usuario": "estoquista1", "senha": "222", "nivel": "estoquista"},
    {"usuario": "rh1", "senha": "333", "nivel": "rh"},
    {"usuario": "cadastrador1", "senha": "444", "nivel": "cadastrador_pecas"},
]

usuario_logado = None

# ======================= FUNÇÕES DE PERSISTÊNCIA =======================

def carregar_dados():
    """Carrega os dados do arquivo JSON para memória"""
    global pecas, servicos, clientes, veiculos, vendas, somaPontos
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            pecas = dados.get('pecas', [])
            servicos = dados.get('servicos', [])
            clientes = dados.get('clientes', [])
            veiculos = dados.get('veiculos', [])
            vendas = dados.get('vendas', [])
            somaPontos = dados.get('somaPontos', 0)
            
def salvar_dados():
    """Salva os dados da memória para o arquivo JSON"""
    dados = {
        'pecas': pecas,
        'servicos': servicos,
        'clientes': clientes,
        'veiculos': veiculos,
        'vendas': vendas,
        'somaPontos': somaPontos
    }
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

# ======================= FUNÇÕES DE USUÁRIO =======================

def realizar_login(username, password):
    """Verifica as credenciais do usuário e realiza o login"""
    global usuario_logado
    user = next((u for u in usuarios if u['usuario'] == username and u['senha'] == password), None)
    if user:
        usuario_logado = user
        return True
    return False

def logout_usuario():
    """Desloga o usuário atual"""
    global usuario_logado
    usuario_logado = None

def get_usuario_logado():
    """Retorna o usuário logado"""
    return usuario_logado

# ======================= FUNÇÕES DE FORMATAÇÃO =======================

def formatar_moeda(valor):
    """Formata um valor numérico para a moeda BRL"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ======================= FUNÇÕES DE CADASTRO =======================

def cadastrar_peca_backend(id_peca, nome_peca, preco_peca, pontuacao_peca):
    """Cadastra uma nova peça no sistema"""
    global pecas
    if any(p['id'] == id_peca for p in pecas):
        return False, "Erro: Peça com este ID já existe!"
    pecas.append({
        "id": id_peca,
        "nome": nome_peca,
        "preco": float(preco_peca),
        "quantidade": 0,
        "pontuacao": int(pontuacao_peca)
    })
    salvar_dados()
    return True, f"Peça '{nome_peca}' cadastrada com sucesso!"

def cadastrar_servico_backend(id_servico, nome_servico, preco_servico):
    """Cadastra um novo serviço no sistema"""
    global servicos
    if any(s['id'] == id_servico for s in servicos):
        return False, "Erro: Serviço com este ID já existe!"
    servicos.append({
        "id": id_servico,
        "nome": nome_servico,
        "preco": float(preco_servico)
    })
    salvar_dados()
    return True, f"Serviço '{nome_servico}' cadastrado com sucesso!"

def cadastrar_cliente_backend(cpf_cliente, nome_cliente, email_cliente):
    """Cadastra um novo cliente no sistema"""
    global clientes
    if any(c['cpf'] == cpf_cliente for c in clientes):
        return False, "Erro: Cliente com este CPF já existe!"
    clientes.append({
        "cpf": cpf_cliente,
        "nome": nome_cliente,
        "email": email_cliente,
    })
    salvar_dados()
    return True, f"Cliente '{nome_cliente}' cadastrado com sucesso!"

def cadastrar_veiculo_backend(placa_veiculo, modelo_veiculo, ano_veiculo):
    """Cadastra um novo veículo no sistema"""
    global veiculos
    if any(v['placa'] == placa_veiculo for v in veiculos):
        return False, "Erro: Veículo com esta placa já existe!"
    veiculos.append({
        "placa": placa_veiculo,
        "modelo": modelo_veiculo,
        "ano": int(ano_veiculo),
    })
    salvar_dados()
    return True, f"Veículo '{placa_veiculo}' cadastrado com sucesso!"

# ======================= FUNÇÕES DE ESTOQUE =======================

def get_estoque():
    """Retorna a lista de todas as peças"""
    return pecas

def aumentar_estoque_backend(peca_id, quantidade_str):
    """Aumenta a quantidade de uma peça no estoque"""
    global pecas
    quantidade = int(quantidade_str)
    peca = next((p for p in pecas if str(p['id']) == str(peca_id)), None)
    if peca:
        peca['quantidade'] += quantidade
        salvar_dados()
        return True, f"Estoque da peça '{peca['nome']}' aumentado em {quantidade}."
    return False, "Peça não encontrada."

# ======================= FUNÇÕES DE VENDAS =======================

def get_item_by_id_and_type(item_id, item_type):
    """Busca um item (peça ou serviço) pelo ID e tipo"""
    if item_type == 'peca':
        return next((p for p in pecas if str(p['id']) == str(item_id)), None)
    elif item_type == 'servico':
        return next((s for s in servicos if str(s['id']) == str(item_id)), None)
    return None

def adicionar_item_pedido(item_id, item_type, quantidade_str):
    """Adiciona um item ao pedido atual"""
    global pedido_atual
    item = get_item_by_id_and_type(item_id, item_type)
    
    if not item:
        return False, "Item não encontrado."

    if item_type == 'peca':
        quantidade = int(quantidade_str)
        if quantidade <= 0 or quantidade > item['quantidade']:
            return False, f"Estoque insuficiente para a peça '{item['nome']}' ou quantidade inválida."
        
        # Verifica se a peça já está no pedido para não duplicar, apenas somar
        item_existente_no_pedido = next((i for i in pedido_atual if i['item']['id'] == item_id and i['tipo'] == 'peca'), None)
        if item_existente_no_pedido:
            item_existente_no_pedido['quantidade'] += quantidade
        else:
            pedido_atual.append({"tipo": item_type, "item": item, "quantidade": quantidade})
        
        return True, f"Peça '{item['nome']}' adicionada ao pedido (x{quantidade})."
    
    elif item_type == 'servico':
        # Para serviços, a quantidade é sempre 1 por adição, mas o serviço pode ser adicionado múltiplas vezes
        pedido_atual.append({"tipo": item_type, "item": item, "quantidade": 1})
        return True, f"Serviço '{item['nome']}' adicionado ao pedido."

def remover_item_pedido(item_index):
    """Remove um item do pedido atual pelo seu índice"""
    global pedido_atual
    try:
        del pedido_atual[int(item_index)]
        return True, "Item removido do pedido."
    except (IndexError, ValueError):
        return False, "Erro ao remover item. Índice inválido."

def get_pedido_atual():
    """Retorna a lista de itens no pedido atual"""
    return pedido_atual

def realizar_venda_backend(pagamento):
    """Finaliza a venda, atualiza o estoque e pontos"""
    global pedido_atual, vendas, somaPontos, pecas
    if not pedido_atual:
        return False, "Nenhum item no pedido para finalizar a venda."

    total_venda = 0
    pontos_ganhos = 0
    itens_vendidos = []

    for item_pedido in pedido_atual:
        item = item_pedido['item']
        tipo = item_pedido['tipo']
        quantidade = item_pedido['quantidade']

        if tipo == 'peca':
            # Atualiza o estoque
            peca_estoque = next((p for p in pecas if p['id'] == item['id']), None)
            if peca_estoque and peca_estoque['quantidade'] >= quantidade:
                peca_estoque['quantidade'] -= quantidade
                total_venda += item['preco'] * quantidade
                pontos_ganhos += item['pontuacao'] * quantidade
                itens_vendidos.append({
                    "tipo": tipo,
                    "item": peca_estoque,
                    "quantidade": quantidade,
                })
            else:
                return False, f"Estoque insuficiente para a peça '{item['nome']}'."
        elif tipo == 'servico':
            total_venda += item['preco'] * quantidade
            itens_vendidos.append({
                "tipo": tipo,
                "item": item,
                "quantidade": quantidade,
            })
    
    # Adiciona os pontos ao total do usuário
    somaPontos += pontos_ganhos

    # Registra a venda
    vendas.append({
        "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "vendedor": usuario_logado['usuario'],
        "itens": itens_vendidos,
        "total": total_venda,
        "pagamento": pagamento,
        "pontos_ganhos": pontos_ganhos
    })

    salvar_dados()
    
    # Limpa o pedido atual após a venda
    pedido_atual.clear()
    
    return True, f"Venda finalizada com sucesso! Total: {formatar_moeda(total_venda)}, Pontos Ganhos: {pontos_ganhos}."

def cancelar_pedido_backend():
    """Cancela o pedido atual"""
    global pedido_atual
    if pedido_atual:
        pedido_atual.clear()
        return True, "Pedido cancelado!"
    return False, "Nenhum pedido para cancelar."

# ======================= FUNÇÕES DE RELATÓRIO =======================

def get_historico_vendas():
    """Retorna o histórico de vendas"""
    return vendas

# ======================= FUNÇÕES DE PONTOS =======================

def get_soma_pontos():
    """Retorna a soma de pontos do usuário logado"""
    return somaPontos

def get_pecas_para_troca():
    """Retorna as peças disponíveis para troca de pontos"""
    return [p for p in pecas if p['quantidade'] > 0] # Apenas peças com estoque

def trocar_pontos_backend(peca_id):
    """Troca pontos por uma peça"""
    global somaPontos
    peca_encontrada = next((p for p in pecas if str(p["id"]) == str(peca_id)), None)

    if not peca_encontrada:
        return False, "Peça não encontrada."
    
    if somaPontos < peca_encontrada['pontuacao']:
        return False, "Você não tem pontos suficientes!"
    
    if peca_encontrada['quantidade'] <= 0:
        return False, f"Estoque insuficiente para a peça '{peca_encontrada['nome']}'."
    
    # Realiza a troca
    somaPontos -= peca_encontrada['pontuacao']
    peca_encontrada['quantidade'] -= 1
    salvar_dados()

    return True, f"Troca realizada com sucesso! Você ganhou uma peça '{peca_encontrada['nome']}' por {peca_encontrada['pontuacao']} pontos."

