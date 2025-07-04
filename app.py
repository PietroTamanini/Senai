import json
import datetime
import os

# ======================= CONSTANTES =======================
ARQUIVO_DADOS = "dados.json"  # Arquivo para armazenamento dos dados

# ======================= VARIÁVEIS GLOBAIS =======================
pecas = []  # Lista de peças cadastradas
servicos = []  # Lista de serviços cadastrados
clientes = []  # Lista de clientes cadastrados
veiculos = []  # Lista de veículos cadastrados
pedido_atual = []  # Itens do pedido em andamento
vendas = []
# Variável para armazenar pontos de venda acumulados
# Histórico de vendas

# Usuários pré-cadastrados
usuarios = [
    {"usuario": "ademiro", "senha": "999", "nivel": "admin"},
    {"usuario": "cara", "senha": "111", "nivel": "atendente"},
]

usuario_logado = None  # Armazena o usuário logado

# ======================= FUNÇÕES DE PERSISTÊNCIA =======================


def carregar_dados():
    """Carrega os dados do arquivo JSON para memória"""
    global pecas, servicos, clientes, veiculos, vendas

    try:
        with open(ARQUIVO_DADOS, "r") as arquivo:
            dados = json.load(arquivo)
            pecas = dados.get("pecas", [])
            servicos = dados.get("servicos", [])
            clientes = dados.get("clientes", [])
            veiculos = dados.get("veiculos", [])
            vendas = dados.get("vendas", [])
        print("Dados carregados com sucesso!")
    except FileNotFoundError:
        print("Arquivo de dados não encontrado. Iniciando com dados vazios.")
    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")


def salvar_dados():
    """Salva os dados atuais no arquivo JSON"""
    dados = {
        "pecas": pecas,
        "servicos": servicos,
        "clientes": clientes,
        "veiculos": veiculos,
        "vendas": vendas,
    }

    try:
        with open(ARQUIVO_DADOS, "w") as arquivo:
            json.dump(dados, arquivo, indent=4)
        print("Dados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar dados: {str(e)}")


# ======================= FUNÇÕES DE AUTENTICAÇÃO =======================


def login():
    """Realiza o login no sistema"""
    global usuario_logado

    print("\n========== LOGIN ==========")
    tentativas = 3

    while tentativas > 0:
        usuario = input("Usuário: ")
        senha = input("Senha: ")

        for user in usuarios:
            if user["usuario"] == usuario and user["senha"] == senha:
                usuario_logado = user
                print(f"\nBem-vindo(a), {usuario}!")
                return True

        tentativas -= 1
        print(f"\nCredenciais incorretas. Tentativas restantes: {tentativas}")

    print("\nNúmero máximo de tentativas atingido. Acesso bloqueado.")
    return False


# ======================= FUNÇÕES AUXILIARES =======================


def formatar_moeda(valor):
    """Formata um valor numérico como moeda"""
    return f"R$ {float(valor):.2f}"


def mostrar_estoque():
    """Exibe o estoque atual de peças"""
    print("\n========== ESTOQUE DE PEÇAS ==========")
    if not pecas:
        print("Nenhuma peça cadastrada.")
        return

    print("{:<10} {:<20} {:<15} {:<10}".format("ID", "Nome", "Preço", "Quantidade"))
    print("-" * 55)
    for peca in pecas:
        print(
            "{:<10} {:<20} {:<15} {:<10}".format(
                peca["id"],
                peca["nome"],
                formatar_moeda(peca["preco"]),
                peca["quantidade"],
            )
        )


def exibir_pedido():
    """Exibe o pedido atual com o total"""
    print("\n========== PEDIDO ATUAL ==========")
    if not pedido_atual:
        print("Nenhum item no pedido.")
        return

    total = 0
    print("{:<5} {:<20} {:<15} {:<10}".format("Qtd", "Item", "Tipo", "Preço"))
    print("-" * 50)

    for item in pedido_atual:
        qtd = item.get("quantidade", 1)
        nome = item["item"]["nome"]
        tipo = item["tipo"].capitalize()
        preco = item["item"]["preco"] * qtd
        total += preco

        print(
            "{:<5} {:<20} {:<15} {:<10}".format(qtd, nome, tipo, formatar_moeda(preco))
        )


# ======================= FUNÇÕES DE CADASTRO =======================


def cadastrar_peca():
    """Cadastra uma nova peça no sistema (apenas admin)"""
    if usuario_logado["nivel"] != "admin":
        print("\nAcesso restrito: apenas administradores podem cadastrar peças.")
        return

    print("\n========== CADASTRAR PEÇA ==========")
    try:
        nova_peca = {
            "id": input("Código da peça: ").strip(),
            "nome": input("Nome: ").strip(),
            "preco": float(input("Preço: ")),
            "quantidade": int(input("Quantidade em estoque: ")),
        }

        if nova_peca["preco"] <= 0 or nova_peca["quantidade"] < 0:
            raise ValueError("Valores devem ser positivos")

        pecas.append(nova_peca)
        salvar_dados()
        print("\nPeça cadastrada com sucesso!")
    except ValueError as e:
        print(f"\nErro: {str(e)}. Certifique-se de inserir valores válidos.")


def cadastrar_servico():
    """Cadastra um novo serviço (apenas admin)"""
    if usuario_logado["nivel"] != "admin":
        print("\nAcesso restrito: apenas administradores podem cadastrar serviços.")
        return

    print("\n========== CADASTRAR SERVIÇO ==========")
    try:
        novo_servico = {
            "id": input("Código do serviço: ").strip(),
            "nome": input("Nome: ").strip(),
            "preco": float(input("Preço: ")),
        }

        if novo_servico["preco"] <= 0:
            raise ValueError("Preço deve ser positivo")

        servicos.append(novo_servico)
        salvar_dados()
        print("\nServiço cadastrado com sucesso!")
    except ValueError as e:
        print(f"\nErro: {str(e)}")


# (Funções para cadastrar clientes e veículos seguem padrão similar)

# ======================= FUNÇÕES DE VENDA =======================


def adicionar_item_pedido(tipo):
    """Adiciona um item (peça ou serviço) ao pedido atual"""
    if tipo == "peça":
        lista_itens = pecas
        nome_lista = "peças"
    else:
        lista_itens = servicos
        nome_lista = "serviços"

    if not lista_itens:
        print(f"\nNenhum(a) {nome_lista} disponível.")
        return

    # Mostra itens disponíveis
    print(f"\n========== {nome_lista.upper()} DISPONÍVEIS ==========")
    for i, item in enumerate(lista_itens, 1):
        print(f"{i}. {item['nome']} ({item['id']}) - {formatar_moeda(item['preco'])}")

    try:
        escolha = int(input(f"\nEscolha o(a) {tipo} (número): ")) - 1
        if escolha < 0 or escolha >= len(lista_itens):
            raise ValueError

        item = lista_itens[escolha]

        if tipo == "peça":
            qtd = int(input("Quantidade: "))
            if qtd <= 0:
                print("Quantidade deve ser positiva!")
                return
            if qtd > item["quantidade"]:
                print("Estoque insuficiente!")
                return
            pedido_atual.append({"tipo": tipo, "item": item, "quantidade": qtd})
        else:
            pedido_atual.append({"tipo": tipo, "item": item})

        print(f"\n{item['nome']} adicionado ao pedido!")
    except (ValueError, IndexError):
        print("\nOpção inválida!")


def finalizar_venda():
    global somaPontos
    somaPontos = 0
    """Finaliza a venda atual"""
    if not pedido_atual:
        print("\nNenhum item no pedido para finalizar.")
        return

    exibir_pedido()

    try:
        confirmacao = input("\nConfirmar venda? (S/N): ").upper()
        if confirmacao != "S":
            print("\nVenda cancelada.")
            return

        # Calcula total
        total = sum(
            item["item"]["preco"] * item.get("quantidade", 1) for item in pedido_atual
        )

        print("Formas de pagamento:\n1 - PIX\n2 - Cartão Crédito\n3 - Cartão Débito")
        pagamento = int(input("Escolha o método: "))

        if pagamento == 1:
            totaldesc = total * (5 / 100)
            total = total - totaldesc

        print("\nData da compra: ", datetime.date.today().strftime("%d/%m/%Y"))
        print("\nHorário da compra: ", datetime.datetime.now().strftime("%H:%M"))
        if total >= 50:
            for i in range(0, len(vendas)):
                somaPontos = somaPontos + 9

        # Registra a venda
        nova_venda = {
            "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "itens": pedido_atual.copy(),
            "total": total,
            "vendedor": usuario_logado["usuario"],
            "pagamento": pagamento,
            "pontos": somaPontos,
        }
        vendas.append(nova_venda)

        # Atualiza estoque
        for item in pedido_atual:
            if item["tipo"] == "peça":
                for peca in pecas:
                    if peca["id"] == item["item"]["id"]:
                        peca["quantidade"] -= item["quantidade"]
                        break

        pedido_atual.clear()
        salvar_dados()
        print("\nVenda registrada com sucesso!")
        print(f"Total: {formatar_moeda(total)}")
        if total < 50 and pagamento == 1 or pagamento == 2 or pagamento == 3:
            print("Você não ganhou pontos nesta compra.")
        else:
            print(f"Você ganhou 9 pontos nesta compra.")

    except Exception as e:
        print(f"\nErro ao finalizar venda: {str(e)}")


# ======================= FUNÇÕES DE RELATÓRIO =======================


def historico_vendas():
    """Exibe o histórico de vendas (apenas admin)"""
    if usuario_logado["nivel"] != "admin":
        print("\nAcesso restrito: apenas administradores podem ver o histórico.")
        return

    print("\n========== HISTÓRICO DE VENDAS ==========")
    if not vendas:
        print("Nenhuma venda registrada.")
        return

    for venda in vendas[::-1]:  # Mostra do mais recente
        print(f"\nData: {venda['data']}")
        print(f"Vendedor: {venda['vendedor']}")
        print("Itens:")
        for item in venda["itens"]:
            print(f"- {item['item']['nome']} ({item['tipo']})")
        print(f"Total: {formatar_moeda(venda['total'])}")
        print("-" * 40)


# ======================= MENUS =======================


def menu_cadastros():
    """Menu de opções de cadastro"""
    while True:
        print("\n========== MENU DE CADASTROS ==========")
        print("1. Cadastrar Peça")
        print("2. Cadastrar Serviço")
        print("3. Cadastrar Cliente")
        print("4. Cadastrar Veículo")
        print("0. Voltar")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            cadastrar_peca()
        elif opcao == "2":
            cadastrar_servico()
        elif opcao == "0":
            break
        else:
            print("\nOpção inválida!")


def menu_vendas():
    """Menu de opções de venda"""
    while True:
        print("\n========== MENU DE VENDAS ==========")
        print("1. Adicionar Peça")
        print("2. Adicionar Serviço")
        print("3. Ver Pedido Atual")
        print("4. Finalizar Venda")
        print("5. Cancelar Pedido")
        print("6. Trocar pontos por peças")
        print("0. Voltar")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            adicionar_item_pedido("peça")
        elif opcao == "2":
            adicionar_item_pedido("serviço")
        elif opcao == "3":
            exibir_pedido()
        elif opcao == "4":
            finalizar_venda()
        elif opcao == "5":
            if pedido_atual:
                confirmacao = input(
                    "\nTem certeza que deseja cancelar o pedido? (S/N): "
                ).upper()
                if confirmacao == "S":
                    pedido_atual.clear()
                    print("\nPedido cancelado!")
            else:
                print("\nNenhum pedido para cancelar.")
        elif opcao == "6":
            trocaPontos()
        elif opcao == "0":
            break
        else:
            print("\nOpção inválida!")


def menu_principal():
    """Menu principal do sistema"""
    while True:
        print("\n========== MENU PRINCIPAL ==========")
        print(f"Usuário: {usuario_logado['usuario']}")
        print("1. Cadastros")
        print("2. Vendas")
        print("3. Estoque")
        print("4. Relatórios")
        print("5. Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            menu_cadastros()
        elif opcao == "2":
            menu_vendas()
        elif opcao == "3":
            mostrar_estoque()
        elif opcao == "4":
            historico_vendas()
        elif opcao == "5":
            print("\nSaindo do sistema...")
            break
        else:
            print("\nOpção inválida!")


def trocaPontos():
    print("\n========== TROCA DE PONTOS ==========")
    print(f"Você tem {somaPontos} pontos acumulados.")
    for peca in pecas:
        print(peca["nome"], " - " + formatar_moeda(peca["preco"]))


# ======================= PROGRAMA PRINCIPAL =======================

if __name__ == "__main__":
    # Carrega os dados ao iniciar
    carregar_dados()

    # Tela de login
    if not login():
        exit()  # Encerra se o login falhar

    # Inicia o menu principal
    menu_principal()

    # Salva os dados ao sair
    salvar_dados()
