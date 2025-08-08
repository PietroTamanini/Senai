# app.py
import json
import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

# ======================= VARIÁVEIS GLOBAIS =======================
usuarios = []
pecas = []
servicos = []
clientes = []
veiculos = []
historico_vendas = []
pedido_atual = []

usuario_logado = None
soma_pontos = 0

# ======================= CONFIGURAÇÃO DA APLICAÇÃO =======================
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_muito_forte_e_unica_aqui_12345'
DATA_FILE = "dados.json"

# ======================= FUNÇÕES DE SUPORTE =======================
def carregar_dados():
    global usuarios, pecas, servicos, clientes, veiculos, historico_vendas
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            usuarios = dados.get('usuarios', [])
            pecas = dados.get('pecas', [])
            servicos = dados.get('servicos', [])
            clientes = dados.get('clientes', [])
            veiculos = dados.get('veiculos', [])
            historico_vendas = dados.get('historico_vendas', [])

def salvar_dados():
    dados = {
        'usuarios': usuarios,
        'pecas': pecas,
        'servicos': servicos,
        'clientes': clientes,
        'veiculos': veiculos,
        'historico_vendas': historico_vendas
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def get_peca_por_id(peca_id):
    for peca in pecas:
        if peca.get('id') == peca_id:
            return peca
    return None

def get_servico_por_id(servico_id):
    for servico in servicos:
        if servico.get('id') == servico_id:
            return servico
    return None

def get_cliente_por_cpf(cliente_cpf):
    for cliente in clientes:
        if cliente.get('cpf') == cliente_cpf:
            return cliente
    return None

def formatar_moeda(valor):
    return f"R$ {float(valor):.2f}".replace('.', ',')

def get_usuario_logado():
    return session.get('usuario_logado')

def get_soma_pontos():
    return session.get('soma_pontos', 0)

# ======================= FUNÇÕES DE BACKEND (LÓGICA DE NEGÓCIO) =======================
def realizar_login(username, password):
    global usuario_logado
    user = next((u for u in usuarios if u['usuario'] == username and u['senha'] == password), None)
    if user:
        session['usuario_logado'] = user
        session['soma_pontos'] = user.get('pontos', 0)
        return True
    return False

def logout_usuario():
    session.pop('usuario_logado', None)
    session.pop('soma_pontos', None)

def aumentar_estoque_backend(peca_id, quantidade_str):
    peca = get_peca_por_id(peca_id)
    if not peca:
        return False, "Erro: Peça não encontrada no sistema."
    
    try:
        quantidade = int(quantidade_str)
        if quantidade <= 0:
            return False, "A quantidade deve ser um número positivo."
    except ValueError:
        return False, "A quantidade deve ser um número inteiro."
    
    peca['quantidade'] += quantidade
    salvar_dados()
    return True, f"Estoque da peça '{peca['nome']}' aumentado em {quantidade} unidade(s)."

def cadastrar_peca_backend(peca_id, nome, preco, pontuacao):
    if get_peca_por_id(peca_id):
        return False, "ID da peça já existe."
    try:
        preco_valido = float(preco.replace(',', '.'))
        pontuacao_valida = int(pontuacao)
    except ValueError:
        return False, "Preço e pontuação devem ser números válidos."
    
    nova_peca = {'id': peca_id, 'nome': nome, 'preco': preco_valido, 'pontuacao': pontuacao_valida, 'quantidade': 0}
    pecas.append(nova_peca)
    salvar_dados()
    return True, f"Peça '{nome}' cadastrada com sucesso!"

def cadastrar_servico_backend(servico_id, nome, preco):
    servico = next((s for s in servicos if s['id'] == servico_id), None)
    if servico:
        return False, "ID do serviço já existe."
    try:
        preco_valido = float(preco.replace(',', '.'))
    except ValueError:
        return False, "Preço deve ser um número válido."
        
    novo_servico = {'id': servico_id, 'nome': nome, 'preco': preco_valido}
    servicos.append(novo_servico)
    salvar_dados()
    return True, f"Serviço '{nome}' cadastrado com sucesso!"

def cadastrar_cliente_backend(cpf, nome, email):
    cliente = next((c for c in clientes if c['cpf'] == cpf), None)
    if cliente:
        return False, "CPF já cadastrado."
    novo_cliente = {'cpf': cpf, 'nome': nome, 'email': email}
    clientes.append(novo_cliente)
    salvar_dados()
    return True, f"Cliente '{nome}' cadastrado com sucesso!"

def cadastrar_veiculo_backend(placa, modelo, ano):
    veiculo = next((v for v in veiculos if v['placa'] == placa), None)
    if veiculo:
        return False, "Placa de veículo já cadastrada."
    novo_veiculo = {'placa': placa, 'modelo': modelo, 'ano': ano}
    veiculos.append(novo_veiculo)
    salvar_dados()
    return True, f"Veículo de placa '{placa}' cadastrado com sucesso!"

def adicionar_item_pedido(item_id, item_type, quantidade_str):
    if item_type == 'peca':
        item = get_peca_por_id(item_id)
        try:
            quantidade = int(quantidade_str) if quantidade_str else 1
        except (ValueError, TypeError):
            return False, "Quantidade inválida para peça."

        if not item:
            return False, "Peça não encontrada."
        if item['quantidade'] < quantidade:
            return False, f"Estoque insuficiente. Disponível: {item['quantidade']}"
        
        pedido_atual.append({'tipo': 'peca', 'item': item, 'quantidade': quantidade})
        return True, f"Peça '{item['nome']}' adicionada ao pedido."

    elif item_type == 'servico':
        item = get_servico_por_id(item_id)
        if not item:
            return False, "Serviço não encontrado."
        
        pedido_atual.append({'tipo': 'servico', 'item': item, 'quantidade': 1})
        return True, f"Serviço '{item['nome']}' adicionado ao pedido."

    return False, "Tipo de item inválido."

def remover_item_pedido(item_index_str):
    try:
        item_index = int(item_index_str)
        if 0 <= item_index < len(pedido_atual):
            item_removido = pedido_atual.pop(item_index)
            return True, f"Item '{item_removido['item']['nome']}' removido do pedido."
        return False, "Índice de item inválido."
    except (ValueError, TypeError):
        return False, "Índice de item inválido."

def cancelar_pedido_backend():
    global pedido_atual
    if not pedido_atual:
        return False, "Não há pedido ativo para cancelar."
    pedido_atual = []
    return True, "Pedido cancelado com sucesso."

def realizar_venda_backend(pagamento, tipo_cliente, cliente_cpf=None):
    global pedido_atual, historico_vendas
    if not pedido_atual:
        return False, "Não há itens no pedido para finalizar a venda."

    if tipo_cliente == 'registrado':
        if not cliente_cpf:
            return False, "Selecione um cliente registrado"
            
        if not clientes:  # Verifica se há clientes cadastrados
            return False, "Nenhum cliente cadastrado no sistema"
            
        cliente = next((c for c in clientes if c['cpf'] == cliente_cpf), None)
        if not cliente:
            return False, "Cliente não encontrado"
            
        cliente_selecionado = cliente.copy()
    else:
        cliente_selecionado = {'cpf': None, 'nome': 'Cliente Não Registrado', 'email': None}

    # Restante da função permanece igual...
    valor_total = 0
    pontos_ganhos = 0
    for item_pedido in pedido_atual:
        item = item_pedido['item']
        quantidade = item_pedido['quantidade']
        valor_total += item['preco'] * quantidade
        
        if item_pedido['tipo'] == 'peca':
            peca_estoque = get_peca_por_id(item['id'])
            if peca_estoque:
                peca_estoque['quantidade'] -= quantidade
            pontos_ganhos += item.get('pontuacao', 0) * quantidade

    # Restante da lógica de desconto e finalização...
    desconto_aplicado = False
    if pagamento == 1:
        valor_total *= 0.95
        desconto_aplicado = True

    nova_venda = {
        'id': len(historico_vendas) + 1,
        'data_hora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'itens': pedido_atual,
        'valor_total': valor_total,
        'pagamento': pagamento,
        'pontos_ganhos': pontos_ganhos,
        'cliente': cliente_selecionado,
        'veiculo': {'marca': '', 'modelo': '', 'ano': ''}
    }
    historico_vendas.append(nova_venda)
    
    usuario = get_usuario_logado()
    if usuario:
        usuario['pontos'] = usuario.get('pontos', 0) + pontos_ganhos
        session['soma_pontos'] = usuario.get('pontos', 0)
    
    salvar_dados()
    pedido_atual = []
    
    mensagem = f"Venda finalizada! Total: {formatar_moeda(valor_total)}. Pontos ganhos: {pontos_ganhos}."
    if desconto_aplicado:
        mensagem += " (5% de desconto aplicado para PIX)."
        
    return True, mensagem

def get_historico_vendas():
    return historico_vendas

def get_estoque():
    return pecas

def get_pedido_atual():
    return pedido_atual

def get_pecas_para_troca():
    return [peca for peca in pecas if peca.get('pontuacao', 0) > 0]

def trocar_pontos_backend(peca_id):
    peca = get_peca_por_id(peca_id)
    usuario = get_usuario_logado()

    if not peca:
        return False, "Peça não encontrada."
    if not usuario:
        return False, "Você precisa estar logado para trocar pontos."

    pontos_necessarios = peca.get('pontuacao', 0)
    pontos_atuais = usuario.get('pontos', 0)

    if pontos_atuais < pontos_necessarios:
        return False, f"Você não tem pontos suficientes para esta troca. Precisa de {pontos_necessarios}."

    if peca['quantidade'] <= 0:
        return False, "Esta peça está fora de estoque."

    # CORREÇÃO AQUI: Diminuir a quantidade em estoque em vez de aumentar
    peca['quantidade'] -= 1  # Reduz 1 do estoque
    usuario['pontos'] -= pontos_necessarios  # Deduz os pontos do usuário
    
    salvar_dados()
    session['soma_pontos'] = usuario.get('pontos', 0)
    return True, f"Peça '{peca['nome']}' trocada com sucesso! Seus novos pontos são {usuario['pontos']}."
# ======================= ROTAS (VIEWS) =======================
@app.context_processor
def inject_globals():
    return dict(
        usuario_logado=get_usuario_logado(),
        somaPontos=get_soma_pontos(),
        formatar_moeda=formatar_moeda,
        clientes=clientes,
        veiculos=veiculos,
        pecas=pecas,
        servicos=servicos
    )

@app.route('/')
def index():
    if get_usuario_logado():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if get_usuario_logado():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if realizar_login(username, password):
            flash(f"Bem-vindo(a), {username}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciais incorretas. Tente novamente.", 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_usuario()
    flash("Você foi desconectado com sucesso.", 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    user = get_usuario_logado()
    if not user:
        flash("Você precisa estar logado para acessar o dashboard.", 'danger')
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_level=user['nivel'])

@app.route('/cadastros', methods=['GET', 'POST'])
def cadastros():
    user = get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "cadastrador_pecas", "rh"]:
        flash("Acesso restrito: você não tem permissão para acessar esta página.", 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        success, msg = False, ""
        
        if form_type == 'peca':
            success, msg = cadastrar_peca_backend(request.form.get('id_peca'), request.form.get('nome_peca'), request.form.get('preco_peca'), request.form.get('pontuacao_peca'))
        elif form_type == 'servico':
            success, msg = cadastrar_servico_backend(request.form.get('id_servico'), request.form.get('nome_servico'), request.form.get('preco_servico'))
        elif form_type == 'cliente':
            success, msg = cadastrar_cliente_backend(request.form.get('cpf_cliente'), request.form.get('nome_cliente'), request.form.get('email_cliente'))
        elif form_type == 'veiculo':
            success, msg = cadastrar_veiculo_backend(request.form.get('placa_veiculo'), request.form.get('modelo_veiculo'), request.form.get('ano_veiculo'))
        
        flash(msg, 'success' if success else 'danger')
        return redirect(url_for('cadastros'))

    return render_template('cadastros.html')

@app.route('/estoque')
def estoque():
    user = get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "estoquista"]:
        flash("Acesso restrito: apenas administradores e estoquistas podem ver o estoque.", 'danger')
        return redirect(url_for('dashboard'))
    return render_template('estoque.html')

@app.route('/aumentar_estoque', methods=['POST'])
def aumentar_estoque():
    user = get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "estoquista"]:
        flash("Acesso restrito: você não tem permissão para aumentar o estoque.", 'danger')
        return redirect(url_for('dashboard'))

    peca_id = request.form.get('peca_id')
    quantidade = request.form.get('quantidade')
    
    success, msg = aumentar_estoque_backend(peca_id, quantidade)
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('estoque'))

@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    user = get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "atendente"]:
        flash("Acesso restrito: apenas administradores e atendentes podem realizar vendas.", 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        success, msg = False, ""
        
        if action == 'add_item':
            item_type = request.form.get('item_type')
            item_id = request.form.get('item_id')
            quantidade_item = request.form.get('quantidade_item')
            success, msg = adicionar_item_pedido(item_id, item_type, quantidade_item)
        elif action == 'cancelar_pedido':
            success, msg = cancelar_pedido_backend()
        elif action == 'remover_item':
            item_index = request.form.get('item_index')
            success, msg = remover_item_pedido(item_index)
        
        flash(msg, 'success' if success else 'danger')
        return redirect(url_for('vendas'))

    total_pedido = sum(item['item']['preco'] * item['quantidade'] for item in pedido_atual)
    return render_template(
        'vendas.html',
        pedido_atual=pedido_atual,
        total_pedido=total_pedido
    )

@app.route('/finalizar_venda', methods=['POST'])
def finalizar_venda():
    user = get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "atendente"]:
        flash("Acesso restrito.", 'danger')
        return redirect(url_for('dashboard'))
    
    pagamento = int(request.form.get('pagamento'))
    tipo_cliente = request.form.get('tipo_cliente')
    cliente_cpf = request.form.get('cliente_cpf') if tipo_cliente == 'registrado' else None
    
    success, msg = realizar_venda_backend(pagamento, tipo_cliente, cliente_cpf)
    
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('vendas'))

@app.route('/relatorios')
def relatorios():
    user = get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "rh"]:
        flash("Acesso restrito: apenas administradores e RH podem ver os relatórios.", 'danger')
        return redirect(url_for('dashboard'))
    
    historico = get_historico_vendas()
    return render_template('relatorios.html', historico=historico)

@app.route('/troca_pontos', methods=['GET', 'POST'])
def troca_pontos():
    user = get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "atendente"]:
        flash("Acesso restrito: apenas administradores e atendentes podem trocar pontos.", 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        peca_id = request.form.get('peca_id')
        success, msg = trocar_pontos_backend(peca_id)
        flash(msg, 'success' if success else 'danger')
        return redirect(url_for('troca_pontos'))

    pecas_para_troca = get_pecas_para_troca()
    pontos_atuais = get_soma_pontos()
    return render_template('troca_pontos.html', pecas=pecas_para_troca, pontos_atuais=pontos_atuais)

# ======================= INICIALIZAÇÃO =======================
if __name__ == '__main__':
    carregar_dados()
    app.run(debug=True)