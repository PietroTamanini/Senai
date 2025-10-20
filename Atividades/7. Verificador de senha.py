senha_correta = 1234
senha_digitada = int(input("Digite a senha: "))
if senha_digitada == senha_correta:
    print("Acesso liberado")
else:
    print("Acesso negado")