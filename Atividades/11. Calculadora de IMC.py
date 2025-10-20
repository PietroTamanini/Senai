peso = float(input("Digite o peso (kg): "))
altura = float(input("Digite a altura (m): "))

imc = peso / (altura ** 2)
imc = round(imc, 2)

print(f"Seu IMC é: {imc}")

if imc < 18.5:
    print("Classificação: Abaixo do peso")
elif imc < 25:
    print("Classificação: Peso normal")
elif imc < 30:
    print("Classificação: Sobrepeso")
elif imc < 35:
    print("Classificação: Obesidade Grau I")
elif imc < 40:
    print("Classificação: Obesidade Grau II")
else:
    print("Classificação: Obesidade Grau III (mórbida)")