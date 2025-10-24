// script.js

// =================================================================
// SIMULAÇÃO DE DADOS GLOBAIS
// =================================================================

// Simulação de Dados de Ponto (CPF, Tipo, Hora)
const pontosDoDia = {
    '00000000000': [ // Aluno Exemplo
        { nome: 'Aluno Exemplo', cpf: '00000000000', tipo: 'ENTRADA', hora: '16:30', data: '2025-10-23' },
        { nome: 'Aluno Exemplo', cpf: '00000000000', tipo: 'SAIDA', hora: '18:30', data: '2025-10-23' }
    ],
    '11122233344': [ // Prof. Alberto
        { nome: 'Prof. Alberto', cpf: '11122233344', tipo: 'ENTRADA', hora: '08:00', data: '2025-10-22' },
        { nome: 'Prof. Alberto', cpf: '11122233344', tipo: 'SAIDA', hora: '12:00', data: '2025-10-22' },
        { nome: 'Prof. Alberto', cpf: '11122233344', tipo: 'ENTRADA', hora: '14:00', data: '2025-10-23' },
        { nome: 'Prof. Alberto', cpf: '11122233344', tipo: 'SAIDA', hora: '18:00', data: '2025-10-23' }
    ],
    '55566677788': [ // Estagiário Lucas
        { nome: 'Estagiário Lucas', cpf: '55566677788', tipo: 'ENTRADA', hora: '09:00', data: '2025-10-23' }
    ]
};

// Simulação de lista de usuários (EDITÁVEL para simular exclusão)
let usuariosSimulados = [
    { nome: 'Administrador Chefe', role: 'ADMIN', cpf: '00000000001' },
    { nome: 'Prof. Alberto', role: 'PROFESSOR', cpf: '11122233344' },
    { nome: 'Estagiário Lucas', role: 'ESTAGIARIO', cpf: '55566677788' },
    { nome: 'Aluno Teste', role: 'ALUNO', cpf: '00000000000' }
];

// =================================================================
// FUNÇÕES UTILITÁRIAS
// =================================================================

function getTodayDate() {
    const now = new Date();
    return now.toISOString().split('T')[0]; // YYYY-MM-DD
}

function getTodayTime() {
    const now = new Date();
    return now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }); // HH:MM
}

function getUserNameByCPF(cpf) {
    const user = usuariosSimulados.find(u => u.cpf === cpf);
    return user ? user.nome : 'Usuário Desconhecido';
}

// =================================================================
// 1. LÓGICA DE LOGIN (index.html)
// =================================================================

function handleLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const alertBox = document.getElementById('login-alert');

    // Mapeamento de Credenciais de Teste
    const credenciais = {
        'admin@lab.com': { role: 'ADMIN', name: 'Administrador Chefe', pass: 'admin' },
        'prof@lab.com': { role: 'PROFESSOR', name: 'Prof. Alberto', pass: 'prof' },
        'estag@lab.com': { role: 'ESTAGIARIO', name: 'Estagiário Lucas', pass: 'estag' },
        'aluno@lab.com': { role: 'ALUNO', name: 'Aluno Teste', pass: 'aluno' },
    };
    
    const user = credenciais[email];

    alertBox.style.display = 'none';

    if (user && user.pass === password) {
        localStorage.setItem('currentUserRole', user.role);
        localStorage.setItem('currentUserName', user.name);
        window.location.href = 'ponto.html';
    } else {
        alertBox.textContent = 'Erro de autenticação. Tente novamente.';
        alertBox.style.display = 'block';
    }
}

// =================================================================
// 2. LÓGICA DE PONTO (ponto.html)
// =================================================================

function determinePontoType(cpf) {
    const pontos = pontosDoDia[cpf] || [];
    const lastPonto = pontos.length > 0 ? pontos[pontos.length - 1] : null;

    // Se não tem ponto ou o último foi SAÍDA, o próximo é ENTRADA.
    // Se o último foi ENTRADA, o próximo é SAÍDA.
    if (!lastPonto || lastPonto.tipo === 'SAIDA') {
        return 'ENTRADA';
    } else {
        return 'SAIDA';
    }
}

function baterPonto() {
    const cpf = document.getElementById('cpf-input').value.trim();
    const messageBox = document.getElementById('ponto-message');
    const nomeUsuario = getUserNameByCPF(cpf);

    // Limpa e oculta a mensagem anterior
    messageBox.style.display = 'none';
    messageBox.classList.remove('action-success', 'alert-danger');
    
    if (cpf.length !== 11 || isNaN(cpf)) {
        messageBox.textContent = 'Por favor, insira um CPF válido (11 dígitos, apenas números).';
        messageBox.classList.add('alert-danger');
        messageBox.style.display = 'block'; 
        return;
    }
    
    // Simulação: Verifica se o CPF existe na base de usuários
    if(nomeUsuario === 'Usuário Desconhecido') {
        messageBox.textContent = 'CPF não encontrado no sistema. Por favor, cadastre-se primeiro.';
        messageBox.classList.add('alert-danger');
        messageBox.style.display = 'block'; 
        return;
    }

    const tipoPonto = determinePontoType(cpf);
    const hora = getTodayTime();

    // Simulação de Registro
    if (!pontosDoDia[cpf]) {
        pontosDoDia[cpf] = [];
    }
    pontosDoDia[cpf].push({ nome: nomeUsuario, cpf: cpf, tipo: tipoPonto, hora: hora, data: getTodayDate() });

    // Feedback visual (CORRIGIDO)
    messageBox.textContent = `${nomeUsuario}, ponto registrado como ${tipoPonto} às ${hora}.`;
    messageBox.classList.add('action-success');
    messageBox.style.display = 'block';

    // Limpa o campo
    document.getElementById('cpf-input').value = '';
    
    console.log("Pontos registrados:", pontosDoDia);
}


// =================================================================
// 3. LÓGICA DE LAYOUT/NAVBAR CONDICIONAL
// =================================================================

function loadNavbar() {
    const userRole = localStorage.getItem('currentUserRole');
    const userName = localStorage.getItem('currentUserName');
    const userContainer = document.getElementById('user-info-container');
    const navLinksContainer = document.getElementById('nav-links-container');

    // Redireciona para login se não estiver logado
    if (!userRole) {
        if(window.location.pathname.endsWith('ponto.html') || window.location.pathname.endsWith('relatorio.html') || window.location.pathname.endsWith('gerenciar_usuarios.html') || window.location.pathname.endsWith('cadastro.html') || window.location.pathname.endsWith('perfil.html')) {
             window.location.href = 'index.html';
             return;
        }
    }

    if(userContainer && userName) {
        userContainer.innerHTML = `
            <div class="user-info">
                <span>${userName} (${userRole})</span>
            </div>
            <a href="perfil.html">
                <img src="https://via.placeholder.com/40?text=${userName.charAt(0)}" alt="Foto de Perfil">
            </a>
        `;
    }

    // Gerenciamento de Links (Navbar)
    if(navLinksContainer) {
        let linksHTML = '';
        
        if (userRole === 'ADMIN') {
             linksHTML = `
                 <a href="ponto.html">Ponto</a>
                 <a href="cadastro.html">Cadastrar Novo Aluno</a>
                 <a href="relatorio.html">Gerar Relatório</a>
                 <a href="gerenciar_usuarios.html">Gerenciar Usuários</a>
             `;
        } else if (userRole === 'PROFESSOR' || userRole === 'ESTAGIARIO') {
             linksHTML = `
                 <a href="ponto.html">Ponto</a>
                 <a href="cadastro.html">Cadastrar Novo Aluno</a>
                 <a href="relatorio.html">Gerar Relatório</a>
                 <a href="gerenciar_usuarios.html">Gerenciar Alunos</a>
             `;
        } else if (userRole === 'ALUNO') {
             // Alunos têm acesso mais restrito
             linksHTML = `
                 <a href="ponto.html">Ponto</a>
                 <a href="relatorio.html">Ver Relatório</a>
             `;
        }
        
        navLinksContainer.innerHTML = linksHTML;
    }
}

// =================================================================
// 4. LÓGICA DE RELATÓRIO (relatorio.html)
// =================================================================

function simulateGenerateReport(reportType) {
    const outputDiv = document.getElementById('relatorio-output');
    outputDiv.innerHTML = '<p style="text-align: center; color: var(--secondary-color);">Gerando relatório...</p>';
    
    let reportData = [];
    let title = "Relatório Geral de Ponto";

    if (reportType === 'GERAL') {
        Object.keys(pontosDoDia).forEach(cpf => {
            reportData = reportData.concat(pontosDoDia[cpf]);
        });
        
    } else if (reportType === 'INDIVIDUAL') {
        const cpfFilterInput = document.getElementById('cpf-filter');
        const cpfFilter = cpfFilterInput ? cpfFilterInput.value.trim() : '';

        if (cpfFilter.length === 0) {
            outputDiv.innerHTML = '<div class="alert alert-danger">Erro: Insira um CPF para o relatório individual.</div>';
            return;
        }
        
        const pontosDoUsuario = pontosDoDia[cpfFilter];
        if (!pontosDoUsuario || pontosDoUsuario.length === 0) {
            outputDiv.innerHTML = `<div class="alert alert-danger">Nenhum ponto encontrado para o CPF: ${cpfFilter}.</div>`;
            return;
        }
        
        reportData = pontosDoUsuario;
        title = `Relatório Individual: ${pontosDoUsuario[0].nome} (CPF: ${cpfFilter})`;
    }
    
    // Ordena os dados por Data e Hora
    reportData.sort((a, b) => {
        if (a.data === b.data) {
            return a.hora.localeCompare(b.hora);
        }
        return a.data.localeCompare(b.data);
    });

    let tableHTML = `
        <h2 style="display: flex; justify-content: space-between; align-items: center; border-bottom: none; padding-bottom: 0;">
            ${title}
        </h2>
        <p style="margin-bottom: 20px;">Pontos registrados (Simulação)</p>
        <table>
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Nome</th>
                    <th>CPF</th>
                    <th>Tipo</th>
                    <th>Hora</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    reportData.forEach(ponto => {
        const rowColor = ponto.tipo === 'ENTRADA' ? 'var(--success-color)' : 'var(--danger-color)';
        tableHTML += `
            <tr>
                <td>${ponto.data}</td>
                <td>${ponto.nome}</td>
                <td>${ponto.cpf}</td>
                <td style="color: ${rowColor}; font-weight: 600;">${ponto.tipo}</td>
                <td>${ponto.hora}</td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    outputDiv.innerHTML = tableHTML;
}

function generatePdfSimulation(reportType) {
    let cpf = '';
    let reportName = 'Relatório Geral';

    if (reportType === 'INDIVIDUAL') {
        const cpfFilterInput = document.getElementById('cpf-filter');
        cpf = cpfFilterInput ? cpfFilterInput.value.trim() : '';
        
        if (cpf.length === 0) {
            alert('Erro: Insira um CPF para gerar o PDF individual.');
            return;
        }
        reportName = `Relatório Individual (CPF: ${cpf})`;
    }
    
    alert(`Simulação de Relatório em PDF: O arquivo "${reportName}" seria gerado e baixado neste momento.`);
}

// =================================================================
// 5. LÓGICA DE GERENCIAR USUÁRIOS (gerenciar_usuarios.html)
// =================================================================

function deleteUserSimulation(cpf, nome) {
    if (confirm(`Tem certeza que deseja EXCLUIR o usuário ${nome} (${cpf})? Esta ação é irreversível!`)) {
        const initialLength = usuariosSimulados.length;
        usuariosSimulados = usuariosSimulados.filter(user => user.cpf !== cpf);
        
        if (usuariosSimulados.length < initialLength) {
             alert(`Usuário ${nome} excluído com sucesso! (Simulação)`);
             loadUserList(); 
        } else {
             alert('Erro ao excluir usuário (CPF não encontrado na simulação).');
        }
    }
}

function loadUserList() {
    const listContainer = document.getElementById('user-list-container');
    if (!listContainer) return;
    
    const currentUserRole = localStorage.getItem('currentUserRole');
    
    let listHTML = '<ul class="user-list">';
    
    let usersToShow = usuariosSimulados;
    if (currentUserRole !== 'ADMIN') {
        // Professor/Estagiário só pode ver e editar 'ALUNO'
        usersToShow = usuariosSimulados.filter(u => u.role === 'ALUNO');
    }
    
    usersToShow.forEach(user => {
        const canEdit = currentUserRole === 'ADMIN' || user.role === 'ALUNO';
        const canDelete = currentUserRole === 'ADMIN' && user.role !== 'ADMIN'; // ADMIN só pode excluir não-ADMINs
        
        listHTML += `
            <li class="user-item">
                <div class="user-item-info">
                    <div class="user-item-name">${user.nome}</div>
                    <div class="user-item-role">Função: ${user.role} | CPF: ${user.cpf}</div>
                </div>
                <div class="user-item-actions">
                    ${canEdit ? `<a href="perfil.html?cpf=${user.cpf}" class="btn btn-primary">Editar</a>` : ''}
                    ${canDelete ? `<button class="btn btn-danger" onclick="deleteUserSimulation('${user.cpf}', '${user.nome}')">Excluir</button>` : ''}
                </div>
            </li>
        `;
    });
    
    listHTML += '</ul>';
    listContainer.innerHTML = listHTML;
}


// =================================================================
// 6. LÓGICA DE PERFIL (perfil.html)
// =================================================================
// Mantida, mas garantindo que exista
function loadProfileInfo() {
    const userName = localStorage.getItem('currentUserName');
    const userRole = localStorage.getItem('currentUserRole');

    const nameDisplay = document.getElementById('profile-name-display');
    const roleDisplay = document.getElementById('profile-role-display');
    const avatarImg = document.getElementById('profile-avatar-img');
    const editName = document.getElementById('edit-name');
    const editEmail = document.getElementById('edit-email');
    const editRole = document.getElementById('edit-role');

    if (nameDisplay) nameDisplay.textContent = userName || 'Usuário Desconhecido';
    if (roleDisplay) roleDisplay.textContent = `Função: ${userRole || 'N/A'}`;
    if (avatarImg) avatarImg.src = `https://via.placeholder.com/150?text=${userName ? userName.charAt(0) : 'U'}`;
    
    if (editName) editName.value = userName || '';
    if (editEmail) editEmail.value = `${userRole.toLowerCase() || 'usuario'}@lab.com`; 
    if (editRole) editRole.value = userRole || ''; 
}


// =================================================================
// INICIALIZAÇÃO E LISTENERS
// =================================================================

window.onload = function() {
    // Listener de Login
    if (document.getElementById('login-form')) {
        document.getElementById('login-form').addEventListener('submit', function(e) {
            e.preventDefault();
            handleLogin();
        });
    }

    // Listener de Bater Ponto
    if (document.getElementById('ponto-form')) {
        document.getElementById('ponto-form').addEventListener('submit', function(e) {
            e.preventDefault();
            baterPonto();
        });
    }
    
    // Carrega Navbar em todas as páginas (exceto index)
    if (!document.getElementById('login-form')) {
        loadNavbar();
    }
    
    // Funções específicas de outras páginas
    if (document.getElementById('user-list-container')) {
        loadUserList();
    }
    
    if (document.getElementById('profile-card')) {
        loadProfileInfo();
    }
    
    // Removida a chamada padrão para o relatório, ele é chamado pelos botões agora.
};