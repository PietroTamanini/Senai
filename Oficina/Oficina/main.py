from flask import Flask, render_template, request, redirect, url_for, session, flash
import app as backend
import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_muito_forte_e_unica_aqui_12345'

# Carrega os dados do arquivo JSON na inicialização
backend.carregar_dados()

@app.context_processor
def inject_user_and_points():
    """Injeta o usuário logado e a soma de pontos em todos os templates"""
    return dict(usuario_logado=backend.get_usuario_logado(), now=datetime.datetime.now, somaPontos=backend.get_soma_pontos())

@app.route('/')
def index():
    """Redireciona para o dashboard se logado, senão para o login"""
    if backend.get_usuario_logado():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para o login de usuários"""
    if backend.get_usuario_logado():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if backend.realizar_login(username, password):
            flash(f"Bem-vindo(a), {backend.get_usuario_logado()['usuario']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciais incorretas. Tente novamente.", 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Rota para deslogar o usuário"""
    backend.logout_usuario()
    flash("Você foi desconectado com sucesso.", 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Rota principal do sistema"""
    user = backend.get_usuario_logado()
    if not user:
        flash("Você precisa estar logado para acessar o dashboard.", 'danger')
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_level=user['nivel'])

@app.route('/cadastros', methods=['GET', 'POST'])
def cadastros():
    """Rota para a página de cadastros (peças, serviços, clientes, veículos)"""
    user = backend.get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "cadastrador_pecas", "rh"]:
        flash("Acesso restrito: você não tem permissão para acessar esta página.", 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        success, msg = False, ""
        if form_type == 'peca':
            success, msg = backend.cadastrar_peca_backend(request.form['id_peca'], request.form['nome_peca'], request.form['preco_peca'], request.form['pontuacao_peca'])
        elif form_type == 'servico':
            success, msg = backend.cadastrar_servico_backend(request.form['id_servico'], request.form['nome_servico'], request.form['preco_servico'])
        elif form_type == 'cliente':
            success, msg = backend.cadastrar_cliente_backend(request.form['cpf_cliente'], request.form['nome_cliente'], request.form['email_cliente'])
        elif form_type == 'veiculo':
            success, msg = backend.cadastrar_veiculo_backend(request.form['placa_veiculo'], request.form['modelo_veiculo'], request.form['ano_veiculo'])
        
        flash(msg, 'success' if success else 'danger')
        return redirect(url_for('cadastros'))

    return render_template('cadastros.html', user_level=user['nivel'], clientes=backend.clientes, veiculos=backend.veiculos)

@app.route('/estoque')
def estoque():
    """Rota para a página de estoque de peças"""
    user = backend.get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "estoquista"]:
        flash("Acesso restrito: apenas administradores e estoquistas podem ver o estoque.", 'danger')
        return redirect(url_for('dashboard'))
    pecas_estoque = backend.get_estoque()
    return render_template('estoque.html', pecas=pecas_estoque, formatar_moeda=backend.formatar_moeda)

@app.route('/aumentar_estoque', methods=['POST'])
def aumentar_estoque():
    """Rota para aumentar o estoque via POST"""
    peca_id = request.form['peca_id']
    quantidade = request.form['quantidade']
    success, msg = backend.aumentar_estoque_backend(peca_id, quantidade)
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('estoque'))

@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    """Rota para a página de vendas"""
    user = backend.get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "atendente"]:
        flash("Acesso restrito: apenas administradores e atendentes podem realizar vendas.", 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_item':
            item_type = request.form.get('item_type')
            item_id = request.form.get('item_id')
            quantity = request.form.get('quantity')
            success, msg = backend.adicionar_item_pedido(item_id, item_type, quantity)
            flash(msg, 'success' if success else 'danger')
            
        elif action == 'cancelar_pedido':
            success, msg = backend.cancelar_pedido_backend()
            flash(msg, 'success' if success else 'danger')

        elif action == 'remover_item':
            item_index = request.form.get('item_index')
            success, msg = backend.remover_item_pedido(item_index)
            flash(msg, 'success' if success else 'danger')
        
        return redirect(url_for('vendas'))

    pecas_disponiveis = backend.get_estoque()
    servicos_disponiveis = backend.servicos
    pedido = backend.get_pedido_atual()
    
    total_pedido = sum(item['item']['preco'] * item['quantidade'] for item in pedido if item['tipo'] == 'peca') + \
                   sum(item['item']['preco'] * item['quantidade'] for item in pedido if item['tipo'] == 'servico')

    return render_template(
        'vendas.html',
        pecas=pecas_disponiveis,
        servicos=servicos_disponiveis,
        pedido_atual=pedido,
        total_pedido=total_pedido,
        formatar_moeda=backend.formatar_moeda
    )

@app.route('/finalizar_venda', methods=['POST'])
def finalizar_venda():
    """Rota para finalizar a venda"""
    user = backend.get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "atendente"]:
        flash("Acesso restrito.", 'danger')
        return redirect(url_for('dashboard'))

    pagamento = int(request.form.get('pagamento'))
    success, msg = backend.realizar_venda_backend(pagamento)
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('vendas'))

@app.route('/relatorios')
def relatorios():
    """Rota para a página de relatórios de vendas"""
    user = backend.get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "rh"]:
        flash("Acesso restrito: apenas administradores e RH podem ver os relatórios.", 'danger')
        return redirect(url_for('dashboard'))

    historico = backend.get_historico_vendas()
    return render_template('relatorios.html', historico=historico, formatar_moeda=backend.formatar_moeda)

@app.route('/troca_pontos', methods=['GET', 'POST'])
def troca_pontos():
    """Rota para a página de troca de pontos"""
    user = backend.get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "atendente"]:
        flash("Acesso restrito: apenas administradores e atendentes podem trocar pontos.", 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        peca_id = request.form['peca_id']
        success, msg = backend.trocar_pontos_backend(peca_id)
        flash(msg, 'success' if success else 'danger')
        return redirect(url_for('troca_pontos'))

    pecas_para_troca = backend.get_pecas_para_troca()
    pontos_atuais = backend.get_soma_pontos()

    return render_template('troca_pontos.html', pecas=pecas_para_troca, pontos_atuais=pontos_atuais)

if __name__ == '__main__':
    app.run(debug=True)
