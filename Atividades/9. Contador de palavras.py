frase = input("Digite uma frase: ").strip()

if frase == "":
    quantidade = 0
else:
    palavras = frase.split()
    quantidade = len(palavras)

print(f"A frase contém {quantidade} palavra(s)")