agenda = {}

while True:
    print("\n=== AGENDA TELEFÔNICA ===")
    print("1. Adicionar contato")
    print("2. Listar todos os contatos")
    print("3. Sair")
    
    opcao = input("Escolha uma opção: ")
    
    if opcao == "1":
        nome = input("Digite o nome: ")
        telefone = input("Digite o telefone: ")
        agenda[nome] = telefone
        print("Contato adicionado com sucesso!")
        
    elif opcao == "2":
        if len(agenda) == 0:
            print("Nenhum contato cadastrado.")
        else:
            print("\n=== LISTA DE CONTATOS ===")
            for nome, telefone in agenda.items():
                print(f"{nome}: {telefone}")
                
    elif opcao == "3":
        print("Saindo do programa...")
        break
        
    else:
        print("Opção inválida! Tente novamente.")