n = int(input("Digite um número: "))
if  n < 0:
    print("Por favor, digite um número não negativo.")
else:
    print("Contagem regressiva: ")
    for i in range(n, -1, -1):
        print(i)
    print("Fogo!")