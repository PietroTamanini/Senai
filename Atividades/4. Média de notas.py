nota1 = print("Digite a primeira nota: ")
nota2 = print("Digite a segunda nota: ")
nota3 = print("Digite a terceira nota: ")
media = nota1 + nota2 + nota3 / 3
if media >= 7:
    print("Aluno APROVADO!")
elif media >= 5:
    print("Aluno em RECUPERAÇÃO!")
else:
    print("Aluno REPROVADO!")