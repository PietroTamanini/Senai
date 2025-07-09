<?php

// Definir o caminho do arquivo de "banco de dados" (JSON)
$arquivoUsuarios = 'usuarios.json';

// --- Funções Auxiliares ---

/**
 * Lê todos os usuários do arquivo JSON.
 * @param string $caminhoArquivo O caminho para o arquivo JSON.
 * @return array Um array de usuários, ou um array vazio se o arquivo não existir ou estiver vazio/inválido.
 */
function lerUsuarios(string $caminhoArquivo): array
{
    if (!file_exists($caminhoArquivo) || filesize($caminhoArquivo) === 0) {
        return []; // Retorna um array vazio se o arquivo não existir ou estiver vazio
    }
    $conteudo = file_get_contents($caminhoArquivo);
    $usuarios = json_decode($conteudo, true); // Decodifica o JSON para um array associativo
    return is_array($usuarios) ? $usuarios : []; // Garante que sempre retorne um array
}

/**
 * Salva a lista de usuários no arquivo JSON.
 * @param string $caminhoArquivo O caminho para o arquivo JSON.
 * @param array $usuarios O array de usuários para salvar.
 * @return bool True em caso de sucesso, false caso contrário.
 */
function salvarUsuarios(string $caminhoArquivo, array $usuarios): bool
{
    $json = json_encode($usuarios, JSON_PRETTY_PRINT); // Codifica para JSON formatado
    return file_put_contents($caminhoArquivo, $json) !== false;
}

// --- Processamento do Formulário ---

$nome = trim($_POST['nome'] ?? '');
$email = trim(strtolower($_POST['email'] ?? '')); // Armazena e-mail em minúsculas
$senha = $_POST['senha'] ?? '';

$mensagensErro = [];

// 1. Validação Básica
if (empty($nome)) {
    $mensagensErro[] = "O campo Nome é obrigatório.";
}
if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $mensagensErro[] = "Por favor, insira um endereço de e-mail válido.";
}
if (empty($senha) || strlen($senha) < 6) {
    $mensagensErro[] = "A senha é obrigatória e deve ter no mínimo 6 caracteres.";
}

// Se houver erros de validação inicial, exibe e para
if (!empty($mensagensErro)) {
    echo "<h1>Erro no Cadastro:</h1>";
    foreach ($mensagensErro as $erro) {
        echo "<p style='color: red;'>$erro</p>";
    }
    echo "<a href='cadastro.html'>Voltar ao Cadastro</a>";
    exit;
}

// 2. Carregar usuários existentes
$usuariosExistentes = lerUsuarios($arquivoUsuarios);

// 3. Verificar se o e-mail já está cadastrado
foreach ($usuariosExistentes as $usuario) {
    if ($usuario['email'] === $email) {
        $mensagensErro[] = "Este e-mail já está cadastrado. Por favor, use outro.";
        break;
    }
}

// Se o e-mail já existe, exibe erro e para
if (!empty($mensagensErro)) {
    echo "<h1>Erro no Cadastro:</h1>";
    echo "<p style='color: red;'>" . $mensagensErro[0] . "</p>"; // Exibe apenas a primeira mensagem de erro específica
    echo "<a href='cadastro.html'>Voltar ao Cadastro</a>";
    exit;
}

// 4. Hash da senha
$senhaHash = password_hash($senha, PASSWORD_DEFAULT);

// 5. Preparar novo usuário
$novoUsuario = [
    'nome' => $nome,
    'email' => $email,
    'senha' => $senhaHash // Armazenar o hash da senha
];

// 6. Adicionar novo usuário e salvar
$usuariosExistentes[] = $novoUsuario;

if (salvarUsuarios($arquivoUsuarios, $usuariosExistentes)) {
    echo "<h1>Cadastro realizado com sucesso!</h1>";
    echo "<p>Bem-vindo(a), " . htmlspecialchars($nome) . "!</p>"; // Usa htmlspecialchars para evitar XSS
    echo "<a href='index.html'>Voltar para o Início</a>";
} else {
    echo "<h1>Erro ao realizar o cadastro.</h1>";
    echo "<p>Não foi possível salvar seus dados. Por favor, tente novamente.</p>";
    echo "<a href='cadastro.html'>Voltar ao Cadastro</a>";
}

?>