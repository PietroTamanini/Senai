<?php
$nome = $_POST['nome'] ?? '';
$email = $_POST['email'] ?? '';
$senha = $_POST['senha'] ?? '';

// Simulação de cadastro
file_put_contents('usuarios.txt', "$nome|$email|$senha\n", FILE_APPEND);

echo "<h1>Cadastro realizado com sucesso!</h1><a href='index.html'>Voltar</a>";
?>