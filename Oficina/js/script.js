/**
 * script.js - Controle principal da aplicação
 * Versão corrigida e otimizada para todas as páginas
 */

document.addEventListener('DOMContentLoaded', function() {
    // =============================================
    // 1. CONTROLE DO MODAL DE ESTOQUE
    // - Este bloco só roda na página de 'estoque.html'
    // =============================================
    const estoqueModal = document.getElementById('aumentarEstoqueModal');

    if (estoqueModal) { // Checa se o modal de estoque existe na página
        // Evento quando o modal é aberto
        estoqueModal.addEventListener('show.bs.modal', function(event) {
            try {
                const button = event.relatedTarget;

                // Extrai dados usando data-bs-* (padrão Bootstrap 5)
                const pecaId = button.getAttribute('data-bs-id');
                const pecaNome = button.getAttribute('data-bs-nome');

                // Atualiza os campos do modal
                const modal = this;
                modal.querySelector('#modalPecaId').value = pecaId;
                modal.querySelector('#modalPecaNome').value = pecaNome;

                // Configura foco automático seguro
                setTimeout(() => {
                    const qtdInput = modal.querySelector('#quantidade');
                    if (qtdInput) {
                        qtdInput.value = 1;
                        qtdInput.focus();
                    }
                }, 150);
            } catch (error) {
                console.error('Erro ao abrir modal de estoque:', error);
            }
        });

        // Limpeza ao fechar o modal
        estoqueModal.addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) form.reset();
        });
    }

    // =============================================
    // 2. CONTROLE DE MENSAGENS FLASH
    // =============================================
    function setupAlerts() {
        document.querySelectorAll('.alert').forEach(alert => {
            // Adiciona botão de fechar
            if (!alert.querySelector('.btn-close')) {
                const closeBtn = document.createElement('button');
                closeBtn.className = 'btn-close';
                closeBtn.setAttribute('data-bs-dismiss', 'alert');
                alert.prepend(closeBtn);
            }

            // Fecha automaticamente após 5s (exceto erros)
            if (!alert.classList.contains('alert-danger')) {
                setTimeout(() => {
                    bootstrap.Alert.getInstance(alert)?.close();
                }, 5000);
            }
        });
    }
    setupAlerts();

    // =============================================
    // 3. CONTROLE DE FORMULÁRIOS
    // - As checagens `if` evitam erros em páginas onde os campos não existem.
    // =============================================
    // Validação de ano do veículo
    const anoInput = document.getElementById('ano_veiculo');
    if (anoInput) {
        anoInput.addEventListener('input', function() {
            const year = parseInt(this.value) || 0;
            const currentYear = new Date().getFullYear();

            if (year > currentYear + 1) {
                this.setCustomValidity('Ano não pode ser futuro');
            } else if (year < 1900) {
                this.setCustomValidity('Ano mínimo é 1900');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Toggle quantidade para serviços
    const itemTypeSelect = document.getElementById('item_type');
    if (itemTypeSelect) { // Checa se o seletor de tipo de item existe
        itemTypeSelect.addEventListener('change', function() {
            const quantityField = document.getElementById('quantity_field');
            if (quantityField) { // Checa se o campo de quantidade existe
                quantityField.style.display = 
                    this.value === 'servico' ? 'none' : 'block';
            }
        });
    }

    // =============================================
    // 4. MODAL DE CONFIRMAÇÃO GENÉRICO
    // - Este bloco só roda se o modal existir na página
    // =============================================
    const genericModal = document.getElementById('confirmModal');
    if (genericModal) {
        genericModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const modalBody = this.querySelector('.modal-body');
            const confirmBtn = this.querySelector('#confirmModalButton');

            if (button && modalBody && confirmBtn) {
                modalBody.textContent = button.getAttribute('data-bs-message') || 'Confirmar ação?';
                const formId = button.getAttribute('data-bs-form-id');

                if (formId) {
                    confirmBtn.onclick = () => {
                        document.getElementById(formId)?.submit();
                    };
                }
            }
        });
    }

    // =============================================
    // 5. DEPURAÇÃO E VERIFICAÇÕES
    // =============================================
    console.log('Sistema inicializado com sucesso!');
    console.log('Bootstrap:', typeof bootstrap !== 'undefined' ? 'OK' : 'Não carregado');
    console.log('Modal de estoque:', estoqueModal ? 'OK' : 'Não encontrado');

    // Verifica conflitos
    if (typeof jQuery !== 'undefined') {
        console.warn('jQuery detectado - Pode causar conflitos com Bootstrap 5');
    }
});