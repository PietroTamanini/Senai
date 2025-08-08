from flask import Flask, render_template, request, redirect, url_for, session, flash
# Importa as classes e funções necessárias do framework Flask.
# - Flask: A classe principal para criar a aplicação web.
# - render_template: Usada para renderizar arquivos HTML (templates).
# - request: Objeto que contém dados da requisição HTTP (formulários, URLs, etc.).
# - redirect: Usada para redirecionar o usuário para outra URL.
# - url_for: Gera uma URL para uma função de view específica.
# - session: Objeto para gerenciar sessões de usuário (dados persistentes entre requisições).
# - flash: Usada para exibir mensagens temporárias para o usuário.

import app as backend # Importa o seu arquivo app.py como backend
# Importa o módulo 'app.py' e o renomeia para 'backend'.
# Isso permite acessar funções e variáveis definidas em 'app.py' usando 'backend.nome_da_funcao'.

import datetime
# Importa o módulo datetime para trabalhar com datas e horas.

app = Flask(__name__)
# Cria uma instância da aplicação Flask.
# '__name__' é uma variável especial do Python que se refere ao nome do módulo atual.
# Isso ajuda o Flask a encontrar recursos como templates e arquivos estáticos.

app.secret_key = 'sua_chave_secreta_muito_forte_e_unica_aqui_12345' # Mantenha esta chave secreta!
# Define uma chave secreta para a aplicação Flask.
# Esta chave é crucial para a segurança de sessões e mensagens flash.
# É fundamental que esta chave seja única, complexa e mantida em segredo em um ambiente de produção.

# Carrega os dados do arquivo JSON na inicialização
backend.carregar_dados()
# Chama a função 'carregar_dados()' do módulo 'backend' (app.py).
# Esta função provavelmente carrega dados de um arquivo JSON para a memória quando a aplicação inicia.

@app.context_processor
def inject_user_and_points():
    """Injeta variáveis em todos os templates"""
    return dict(
        usuario_logado=backend.get_usuario_logado(),
        now=datetime.datetime.now,
        somaPontos=backend.get_soma_pontos(),
        formatar_moeda=backend.formatar_moeda,
        clientes=backend.clientes,  # Adicionando a lista de clientes
        veiculos=backend.veiculos,  # Opcional: se precisar em outros templates
        pecas=backend.pecas,       # Opcional: se precisar em outros templates
        servicos=backend.servicos   # Opcional: se precisar em outros templates
    )

@app.route('/')
# Decorador que associa a função 'index' à URL raiz ('/').
def index():
    """Redireciona para o dashboard se logado, senão para o login"""
    # Define a função de view para a rota raiz.
    if backend.get_usuario_logado():
        # Verifica se há um usuário logado chamando a função do backend.
        return redirect(url_for('dashboard'))
        # Se houver, redireciona para a rota 'dashboard'.
    return redirect(url_for('login'))
    # Se não houver usuário logado, redireciona para a rota 'login'.

@app.route('/login', methods=['GET', 'POST'])
# Decorador que associa a função 'login' à URL '/login'.
# Permite requisições GET (para exibir o formulário) e POST (para submeter o formulário).
def login():
    """Rota para o login de usuários"""
    # Define a função de view para a rota de login.
    if backend.get_usuario_logado():
        # Se o usuário já estiver logado.
        return redirect(url_for('dashboard'))
        # Redireciona para o dashboard.
    if request.method == 'POST':
        # Se a requisição for do tipo POST (formulário submetido).
        username = request.form['username']
        # Obtém o valor do campo 'username' do formulário.
        password = request.form['password']
        # Obtém o valor do campo 'password' do formulário.
        if backend.realizar_login(username, password):
            # Chama a função 'realizar_login' do backend para autenticar o usuário.
            flash(f"Bem-vindo(a), {backend.get_usuario_logado()['usuario']}!", 'success')
            # Exibe uma mensagem de sucesso com o nome do usuário.
            return redirect(url_for('dashboard'))
            # Redireciona para o dashboard.
        else:
            # Se as credenciais estiverem incorretas.
            flash("Credenciais incorretas. Tente novamente.", 'danger')
            # Exibe uma mensagem de erro.
    return render_template('login.html')
    # Renderiza o template 'login.html' (para requisições GET ou falha de login POST).

@app.route('/logout')
# Decorador que associa a função 'logout' à URL '/logout'.
def logout():
    """Rota para deslogar o usuário"""
    # Define a função de view para a rota de logout.
    backend.logout_usuario()
    # Chama a função 'logout_usuario' do backend para encerrar a sessão do usuário.
    flash("Você foi desconectado com sucesso.", 'info')
    # Exibe uma mensagem informativa.
    return redirect(url_for('login'))
    # Redireciona para a página de login.

@app.route('/dashboard')
# Decorador que associa a função 'dashboard' à URL '/dashboard'.
def dashboard():
    """Rota principal do sistema"""
    # Define a função de view para a rota do dashboard.
    user = backend.get_usuario_logado()
    # Obtém o usuário logado do backend.
    if not user:
        # Se não houver usuário logado.
        flash("Você precisa estar logado para acessar o dashboard.", 'danger')
        # Exibe uma mensagem de erro.
        return redirect(url_for('login'))
        # Redireciona para a página de login.
    return render_template('dashboard.html', user_level=user['nivel'])
    # Renderiza o template 'dashboard.html', passando o nível do usuário para o template.

@app.route('/cadastros', methods=['GET', 'POST'])
# Decorador que associa a função 'cadastros' à URL '/cadastros'.
# Permite requisições GET e POST.
def cadastros():
    """Rota para a página de cadastros (peças, serviços, clientes, veículos)"""
    # Define a função de view para a rota de cadastros.
    user = backend.get_usuario_logado()
    # Obtém o usuário logado.
    if not user or user['nivel'] not in ["admin", "cadastrador_pecas", "rh"]:
        # Verifica se o usuário está logado e se tem um dos níveis de acesso permitidos.
        flash("Acesso restrito: você não tem permissão para acessar esta página.", 'danger')
        # Exibe uma mensagem de acesso restrito.
        return redirect(url_for('dashboard'))
        # Redireciona para o dashboard.

    if request.method == 'POST':
        # Se a requisição for do tipo POST (formulário de cadastro submetido).
        form_type = request.form.get('form_type')
        # Obtém o tipo de formulário (peca, servico, cliente, veiculo) do campo oculto.
        success, msg = False, ""
        # Inicializa variáveis para o resultado da operação.
        if form_type == 'peca':
            # Se o formulário for de cadastro de peça.
            success, msg = backend.cadastrar_peca_backend(request.form['id_peca'], request.form['nome_peca'], request.form['preco_peca'], request.form['pontuacao_peca'])
            # Chama a função do backend para cadastrar a peça.
        elif form_type == 'servico':
            # Se o formulário for de cadastro de serviço.
            success, msg = backend.cadastrar_servico_backend(request.form['id_servico'], request.form['nome_servico'], request.form['preco_servico'])
            # Chama a função do backend para cadastrar o serviço.
        elif form_type == 'cliente':
            # Se o formulário for de cadastro de cliente.
            success, msg = backend.cadastrar_cliente_backend(request.form['cpf_cliente'], request.form['nome_cliente'], request.form['email_cliente'])
            # Chama a função do backend para cadastrar o cliente.
        elif form_type == 'veiculo':
            # Se o formulário for de cadastro de veículo.
            success, msg = backend.cadastrar_veiculo_backend(request.form['placa_veiculo'], request.form['modelo_veiculo'], request.form['ano_veiculo'])
            # Chama a função do backend para cadastrar o veículo.
        
        flash(msg, 'success' if success else 'danger')
        # Exibe a mensagem de sucesso ou erro retornada pelo backend.
        return redirect(url_for('cadastros'))
        # Redireciona de volta para a página de cadastros.

    return render_template('cadastros.html', user_level=user['nivel'], clientes=backend.clientes, veiculos=backend.veiculos)
    # Renderiza o template 'cadastros.html', passando o nível do usuário, a lista de clientes e a lista de veículos.

@app.route('/estoque')
# Decorador que associa a função 'estoque' à URL '/estoque'.
def estoque():
    """Rota para a página de estoque de peças"""
    # Define a função de view para a rota de estoque.
    user = backend.get_usuario_logado()
    # Obtém o usuário logado.
    if not user or user['nivel'] not in ["admin", "estoquista"]:
        # Verifica se o usuário está logado e se tem permissão de administrador ou estoquista.
        flash("Acesso restrito: apenas administradores e estoquistas podem ver o estoque.", 'danger')
        # Exibe uma mensagem de acesso restrito.
        return redirect(url_for('dashboard'))
        # Redireciona para o dashboard.
    pecas_estoque = backend.get_estoque()
    # Obtém a lista de peças em estoque do backend.
    return render_template('estoque.html', pecas=pecas_estoque) # formatar_moeda já injetado
    # Renderiza o template 'estoque.html', passando a lista de peças.
    # (A função formatar_moeda já está disponível via context_processor).

@app.route('/aumentar_estoque', methods=['POST'])
# Decorador que associa a função 'aumentar_estoque' à URL '/aumentar_estoque'.
# Permite apenas requisições POST.
def aumentar_estoque():
    """Rota para aumentar o estoque via POST"""
    # Define a função de view para a rota de aumentar estoque.
    user = backend.get_usuario_logado()
    # Obtém o usuário logado.
    if not user or user['nivel'] not in ["admin", "estoquista"]:
        # Verifica se o usuário está logado e se tem permissão de administrador ou estoquista.
        flash("Acesso restrito: você não tem permissão para aumentar o estoque.", 'danger')
        # Exibe uma mensagem de acesso restrito.
        return redirect(url_for('dashboard'))
        # Redireciona para o dashboard.

    peca_id = request.form['peca_id']
    # Obtém o ID da peça do formulário.
    quantidade = request.form['quantidade']
    # Obtém a quantidade do formulário.
    success, msg = backend.aumentar_estoque_backend(peca_id, quantidade)
    # Chama a função do backend para aumentar o estoque.
    flash(msg, 'success' if success else 'danger')
    # Exibe a mensagem de sucesso ou erro.
    return redirect(url_for('estoque'))
    # Redireciona de volta para a página de estoque.

@app.route('/vendas', methods=['GET', 'POST'])
# Decorador que associa a função 'vendas' à URL '/vendas'.
# Permite requisições GET e POST.
def vendas():
    """Rota para a página de vendas"""
    # Define a função de view para a rota de vendas.
    user = backend.get_usuario_logado()
    # Obtém o usuário logado.
    if not user or user['nivel'] not in ["admin", "atendente"]:
        # Verifica se o usuário está logado e se tem permissão de administrador ou atendente.
        flash("Acesso restrito: apenas administradores e atendentes podem realizar vendas.", 'danger')
        # Exibe uma mensagem de acesso restrito.
        return redirect(url_for('dashboard'))
        # Redireciona para o dashboard.

    if request.method == 'POST':
        # Se a requisição for do tipo POST.
        action = request.form.get('action')
        # Obtém a ação a ser realizada (add_item, cancelar_pedido, remover_item).
        
        if action == 'add_item':
            # Se a ação for adicionar item.
            item_type = request.form.get('item_type')
            # Obtém o tipo de item (peça ou serviço).
            item_id = request.form.get('item_id')
            # Obtém o ID do item.
            quantity = request.form.get('quantity')
            # Obtém a quantidade.
            success, msg = backend.adicionar_item_pedido(item_id, item_type, quantity)
            # Chama a função do backend para adicionar o item ao pedido.
            flash(msg, 'success' if success else 'danger')
            # Exibe a mensagem de sucesso ou erro.
            
        elif action == 'cancelar_pedido':
            # Se a ação for cancelar pedido.
            success, msg = backend.cancelar_pedido_backend()
            # Chama a função do backend para cancelar o pedido.
            flash(msg, 'success' if success else 'danger')
            # Exibe a mensagem de sucesso ou erro.

        elif action == 'remover_item':
            # Se a ação for remover item.
            item_index = request.form.get('item_index')
            # Obtém o índice do item a ser removido.
            success, msg = backend.remover_item_pedido(item_index)
            # Chama a função do backend para remover o item.
            flash(msg, 'success' if success else 'danger')
            # Exibe a mensagem de sucesso ou erro.
        
        return redirect(url_for('vendas'))
        # Redireciona de volta para a página de vendas após a ação.

    pecas_disponiveis = backend.get_estoque()
    # Obtém as peças disponíveis do estoque.
    servicos_disponiveis = backend.servicos
    # Obtém os serviços disponíveis.
    pedido = backend.get_pedido_atual()
    # Obtém o pedido atual.
    
    total_pedido = sum(item['item']['preco'] * item['quantidade'] for item in pedido)
    # Calcula o total do pedido somando o preço * quantidade de cada item.

    return render_template(
        'vendas.html',
        pecas=pecas_disponiveis,
        servicos=servicos_disponiveis,
        pedido_atual=pedido,
        total_pedido=total_pedido
    )
    # Renderiza o template 'vendas.html', passando as peças, serviços, pedido atual e total do pedido.

@app.route('/finalizar_venda', methods=['POST'])
def finalizar_venda():
    user = backend.get_usuario_logado()
    if not user or user['nivel'] not in ["admin", "atendente"]:
        flash("Acesso restrito.", 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        pagamento = int(request.form.get('pagamento'))
        tipo_cliente = request.form.get('tipo_cliente')
        
        # Validação adicional para cliente registrado
        if tipo_cliente == 'registrado':
            cliente_cpf = request.form.get('cliente_cpf')
            if not cliente_cpf:
                flash("Por favor, selecione um cliente registrado", 'danger')
                return redirect(url_for('vendas'))
        else:
            cliente_cpf = None
        
        success, msg = backend.realizar_venda_backend(pagamento, tipo_cliente, cliente_cpf)
    except Exception as e:
        flash(f"Erro ao processar venda: {str(e)}", 'danger')
        return redirect(url_for('vendas'))
    
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('vendas'))

@app.route('/relatorios')
# Decorador que associa a função 'relatorios' à URL '/relatorios'.
def relatorios():
    """Rota para a página de relatórios de vendas"""
    # Define a função de view para a rota de relatórios.
    user = backend.get_usuario_logado()
    # Obtém o usuário logado.
    if not user or user['nivel'] not in ["admin", "rh"]:
        # Verifica permissão.
        flash("Acesso restrito: apenas administradores e RH podem ver os relatórios.", 'danger')
        # Exibe mensagem de acesso restrito.
        return redirect(url_for('dashboard'))
        # Redireciona para o dashboard.

    historico = backend.get_historico_vendas()
    # Obtém o histórico de vendas do backend.
    return render_template('relatorios.html', historico=historico)
    # Renderiza o template 'relatorios.html', passando o histórico de vendas.

@app.route('/troca_pontos', methods=['GET', 'POST'])
# Decorador que associa a função 'troca_pontos' à URL '/troca_pontos'.
# Permite requisições GET e POST.
def troca_pontos():
    """Rota para a página de troca de pontos"""
    # Define a função de view para a rota de troca de pontos.
    user = backend.get_usuario_logado()
    # Obtém o usuário logado.
    if not user or user['nivel'] not in ["admin", "atendente"]:
        # Verifica permissão.
        flash("Acesso restrito: apenas administradores e atendentes podem trocar pontos.", 'danger')
        # Exibe mensagem de acesso restrito.
        return redirect(url_for('dashboard'))
        # Redireciona para o dashboard.

    if request.method == 'POST':
        # Se a requisição for do tipo POST.
        peca_id = request.form['peca_id']
        # Obtém o ID da peça do formulário.
        success, msg = backend.trocar_pontos_backend(peca_id)
        # Chama a função do backend para realizar a troca de pontos.
        flash(msg, 'success' if success else 'danger')
        # Exibe a mensagem de sucesso ou erro.
        return redirect(url_for('troca_pontos'))
        # Redireciona de volta para a página de troca de pontos.

    pecas_para_troca = backend.get_pecas_para_troca()
    # Obtém as peças disponíveis para troca do backend.
    pontos_atuais = backend.get_soma_pontos()
    # Obtém a soma de pontos atual do usuário logado.

    return render_template('troca_pontos.html', pecas=pecas_para_troca, pontos_atuais=pontos_atuais)
    # Renderiza o template 'troca_pontos.html', passando as peças para troca e os pontos atuais.

if __name__ == '__main__':
    # Bloco que só é executado se o script for executado diretamente (não importado como módulo).
    app.run(host='0.0.0.0', port=6742)
    # Inicia o servidor de desenvolvimento do Flask.
    # 'debug=True' ativa o modo de depuração, que fornece mensagens de erro detalhadas
    # e recarrega o servidor automaticamente a cada alteração no código.
    # DEVE SER DESATIVADO EM PRODUÇÃO por questões de segurança.
