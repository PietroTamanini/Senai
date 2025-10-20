senha_correta = 1234
max_tentativas = 3
tentativas = 0

print("=== SISTEMA DE ACESSO ===")

while tentativas < max_tentativas:
    tentativas_restantes = max_tentativas - tentativas
    senha_digitada = int(input(f"Digite a senha ({tentativas_restantes} tentativa(s) restante(s)): "))
    tentativas += 1
    
    if senha_digitada == senha_correta:
        print("Acesso liberado!")
        break
    else:
        print("Senha incorreta!")
        if tentativas < max_tentativas:
            print("Tente novamente.")
else:
    print("Acesso bloqueado! Número máximo de tentativas excedido.")