palavra = input("Digite uma palavra: ").lower()
vogais = []
consoantes = []
for letra in palavra:
    if letra.isalpha():
        if letra in 'aeiou':
            vogais.append(letra)
        else:
            consoantes.append(letra)
print("Vogais: ", vogais)
print("consoantes: ", consoantes)