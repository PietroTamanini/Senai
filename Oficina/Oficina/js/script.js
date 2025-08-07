        itemTypeSelect.addEventListener('change', toggleQuantityField);
        // Chama a função uma vez ao carregar a página para definir o estado inicial
        toggleQuantityField();
    }
    // Função para confirmar exclusão/cancelamento
    var confirmButtons = document.querySelectorAll('.confirm-action');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            var message = this.dataset.confirmMessage || 'Tem certeza que deseja realizar esta ação?';
            if (!confirm(message)) {
                event.preventDefault(); // Impede o envio do formulário
            }
        });
    });
    // Auto-fechar alertas após alguns segundos
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        if (!alert.classList.contains('alert-dismissible')) { // Não auto-fecha se já tiver botão de fechar
            setTimeout(function() {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000); // Fecha após 5 segundos
        }
    });
    // Adicionar validação para o ano do veículo (exemplo)
    var anoVeiculoInput = document.getElementById('ano_veiculo');
    if (anoVeiculoInput) {
        anoVeiculoInput.addEventListener('input', function() {
            var currentYear = new Date().getFullYear();
            if (parseInt(this.value) > (currentYear + 1)) {
                this.setCustomValidity('O ano não pode ser futuro.');
            } else if (parseInt(this.value) < 1900) {
                this.setCustomValidity('O ano deve ser a partir de 1900.');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});