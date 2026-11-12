// ==========================================================================
// APP.JS - Lógica de renderização da interface-base (CONGELADA - Módulo 6)
// Lê config/tasks.json e renderiza T01-T04 em sequência
// Implementa fluxo de dois passos: selecionar → confirmar
// ==========================================================================

const appState = {
    currentTaskIndex: 0,
    tasks: [],
    selectedDecision: null
};

async function init() {
    try {
        const response = await fetch('config/tasks.json');
        const data = await response.json();
        appState.tasks = data.tasks;
        renderTask();
    } catch (error) {
        console.error('Erro ao carregar tarefas:', error);
    }
}

function renderTask() {
    const task = appState.tasks[appState.currentTaskIndex];
    if (!task) return;
    
    const container = document.getElementById('task-container');
    const request = task.request;
    const hasJustification = request.justification && request.justification.trim() !== '';
    
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <span class="card-title" id="request_id">${request.request_id}</span>
                <span class="badge" id="priority_badge">${request.priority}</span>
            </div>
            
            ${!hasJustification ? `
                <div class="alert alert-error">
                    Justificativa ausente
                </div>
            ` : ''}
            
            <div class="task-info">
                <div class="info-row">
                    <span class="info-label">Valor:</span>
                    <span class="info-value" id="request_value">${request.value}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Impacto:</span>
                    <span class="info-value" id="request_impact">${request.impact}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Prazo:</span>
                    <span class="info-value" id="request_deadline">${request.deadline}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Custo:</span>
                    <span class="info-value" id="request_cost">${request.cost}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Justificativa:</span>
                    <span class="info-value" id="request_justification">${hasJustification ? request.justification : 'Ausente'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Histórico:</span>
                    <span class="info-value" id="request_history">${request.history}</span>
                </div>
            </div>
            
            <div class="task-actions">
                <div class="button-group">
                    <button class="button" id="btn_approve" onclick="selectDecision('approve')">Aprovar</button>
                    <button class="button" id="btn_adjust" onclick="selectDecision('request_adjustments')">Solicitar Ajustes</button>
                    <button class="button" id="btn_reject" onclick="selectDecision('reject')">Rejeitar</button>
                </div>
                <div class="button-group" style="margin-top: var(--spacing-md);">
                    <button class="button" id="btn_confirm" onclick="confirmDecision()" disabled>Confirmar</button>
                </div>
            </div>
        </div>
    `;
    
    appState.selectedDecision = null;
}

function selectDecision(decision) {
    appState.selectedDecision = decision;
    
    document.getElementById('btn_approve').classList.remove('button-selected');
    document.getElementById('btn_adjust').classList.remove('button-selected');
    document.getElementById('btn_reject').classList.remove('button-selected');
    
    const buttonMap = {
        'approve': 'btn_approve',
        'request_adjustments': 'btn_adjust',
        'reject': 'btn_reject'
    };
    
    document.getElementById(buttonMap[decision]).classList.add('button-selected');
    document.getElementById('btn_confirm').disabled = false;
}

function confirmDecision() {
    if (!appState.selectedDecision) return;
    
    console.log(`Decisão confirmada: ${appState.selectedDecision}`);
    
    appState.currentTaskIndex++;
    
    if (appState.currentTaskIndex < appState.tasks.length) {
        renderTask();
    } else {
        document.getElementById('task-container').innerHTML = `
            <div class="card">
                <p>Obrigado por participar do experimento.</p>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', init);