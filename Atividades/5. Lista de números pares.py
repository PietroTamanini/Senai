n = int(input("Digite um número inteiro: "))
lista_pares = []
if n < 2:
    print(f"Não há números pares entre 1 e {n}")
else:
    for i in range(1, n + 1):
        if i % 2 == 0:
            lista_pares.append(i)
    print(f"Números pares de 1 até {n}: ")
    print(lista_pares)