import random

numero_secreto = random.randint(1, 20)
tentativas = 0

print("=== JOGO DE ADIVINHAÇÃO ===")
print("Tente adivinhar o número entre 1 e 20")

while True:
    palpite = int(input("Digite seu palpite: "))
    tentativas += 1
    
    if palpite < numero_secreto:
        print(f"O número secreto é MAIOR que {palpite}")
    elif palpite > numero_secreto:
        print(f"O número secreto é MENOR que {palpite}")
    else:
        print(f"PARABÉNS! Você acertou em {tentativas} tentativa(s)")
        print(f"O número secreto era {numero_secreto}")
        break