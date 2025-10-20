import os
import platform

biblioteca = []

def limpar():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
        
def cadastrar_livro():
    print("Cadastro de livros📙")
    nome = input("Digite o nome do livro: ")
    preco = float(input("Digite o preço do livro: "))
    genero = input("Digite o gênero do livro: ")
    autor = input("Digite o nome do autor: ")
        
    Livro = {
            "nome": nome,
            "preco": preco,
            "genero": genero,
            "autor": autor
        }
    biblioteca.append(Livro)
    print("Livro adicionado com sucesso!✅")
    input("Pressione Enter para voltar ao menu.")
    limpar()

def listar_livros():
    print("Listagem de livros🗒️")
    if not biblioteca:
            print("Nenhum livro cadastrado ainda❌")
            input("Pressione Enter para voltar ao menu.")
            limpar()
    for livro in biblioteca:
        print(f"Nome: {livro["nome"]} ")
        print(f"preco: {livro["preco"]} ")
        print(f"Autor: {livro["autor"]} ")
        print(f"Gênero: {livro["genero"]}\n")
        input("Pressione Enter para voltar ao menu.")
        limpar()
            
def excluir_livros():
    print("Excluir livros🗑️")
    if not biblioteca:
            print("Nenhum livro para excluir❌")
            input("Pressione Enter para voltar ao menu.")
            limpar()
            return
    for i, Livro in enumerate(biblioteca):
        print(f"Número {i}")
        print(f"Nome: {Livro["nome"]} ")
        print(f"Proço: {Livro["preco"]} ")
        print(f"Autor: {Livro["autor"]} ")
        print(f"Gênero: {Livro["genero"]} ")
            
    numero_livro = int(input("Qual livro você quer excluir? "))
    print("Livro excluído com sucesso!✅")
    input("Pressione Enter para voltar ao menu.")
    limpar()
    biblioteca.pop(numero_livro)

while True:
    print("Biblioteca📚")
    print("1- Cadastrar livros📙")
    print("2- Listar livros🗒️")
    print("3- Excluir livros🗑️")
    print("4- Sair")

    escolha = int(input("Escolha uma opção: "))
    limpar()
    
    if escolha == 1:
        cadastrar_livro()
    elif escolha == 2:
        listar_livros()
    elif escolha == 3:
        excluir_livros()
    elif escolha == 4: 
        print("Volte sempre!😊")
        break
    else:
        print("Opção inválida!❌")       