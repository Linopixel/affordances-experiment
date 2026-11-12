// ==========================================================================
// A.JS - Derivação A (Experimental)
// Renderiza o layout A com suporte a microinterações do botão Confirmar + EventLogger
// ==========================================================================

function renderTask() {
    var task = appState.tasks[appState.currentTaskIndex];
    if (!task) return;

    var container = document.getElementById('task-container');
    var request = task.request;

    var hasJustification = request.justification && request.justification.trim() !== '';

    var priorityClassMap = { 'Alta': 'tag--high', 'Média': 'tag--medium', 'Baixa': 'tag--low' };
    var priorityClass = priorityClassMap[request.priority] || 'tag--high';

    var priorityIconMap = { 'Alta': '\u25B2', 'Média': '\u25C6', 'Baixa': '\u25BC' };
    var priorityIcon = priorityIconMap[request.priority] || '\u25B2';

    container.innerHTML = ''
        + '<article class="card">'
        +   '<header class="card__header">'
        +       '<h2 class="card__id" id="request_id">' + request.request_id + '</h2>'
        +       '<span class="tag ' + priorityClass + '" id="priority_badge">'
        +           '<span aria-hidden="true">' + priorityIcon + '</span> '
        +           '<span class="tag__k">Prioridade:</span> '
        +           request.priority
        +       '</span>'
        +   '</header>'
        +   (!hasJustification
                ? '<div class="alert-banner" role="alert">'
                    + '<span aria-hidden="true">\u26A0</span>'
                    + '<span>Justificativa ausente</span>'
                  + '</div>'
                : '')
        +   '<section class="section">'
        +       '<dl class="facts">'
        +           '<div class="facts__valor"><dt>Valor</dt><dd id="request_value">' + request.value + '</dd></div>'
        +           '<div><dt>Custo</dt><dd id="request_cost">' + request.cost + '</dd></div>'
        +           '<div><dt>Impacto</dt><dd id="request_impact">' + request.impact + '</dd></div>'
        +           '<div><dt>Prazo</dt><dd id="request_deadline">' + request.deadline + '</dd></div>'
        +       '</dl>'
        +   '</section>'
        +   '<section class="section">'
        +       '<dl>'
        +           '<div class="text-block">'
        +               '<dt>Justificativa</dt>'
        +               '<dd id="request_justification"' + (hasJustification ? '' : ' class="is-empty"') + '>'
        +                   (hasJustification ? request.justification : 'Ausente')
        +               '</dd>'
        +           '</div>'
        +           '<div class="text-block">'
        +               '<dt>Histórico</dt>'
        +               '<dd id="request_history">' + request.history + '</dd>'
        +           '</div>'
        +       '</dl>'
        +   '</section>'
        +   '<div class="actions">'
        +       '<div class="group" role="group" aria-label="Decisão" id="decisoes">'
        +           '<button type="button" class="btn btn--approve" id="btn_approve" data-decision-btn aria-pressed="false" onclick="selectDecision(\'approve\')">'
        +               '<span class="check" aria-hidden="true">\u2713</span>Aprovar'
        +           '</button>'
        +           '<button type="button" class="btn btn--adjust" id="btn_adjust" data-decision-btn aria-pressed="false" onclick="selectDecision(\'request_adjustments\')">'
        +               '<span class="check" aria-hidden="true">\u2713</span>Solicitar Ajustes'
        +           '</button>'
        +           '<button type="button" class="btn btn--reject" id="btn_reject" data-decision-btn aria-pressed="false" onclick="selectDecision(\'reject\')">'
        +               '<span class="check" aria-hidden="true">\u2713</span>Rejeitar'
        +           '</button>'
        +       '</div>'
        +       '<div class="confirm-area">'
        +           '<button type="button" class="btn btn--confirm" id="btn_confirm" onclick="confirmDecision()" aria-disabled="true" disabled>'
        +               '<span class="slot" aria-hidden="true">'
        +                   '<span id="seta">\u2192</span>'
        +                   '<span id="ok" hidden>\u2713</span>'
        +               '</span>'
        +               '<span>Confirmar</span>'
        +           '</button>'
        +       '</div>'
        +   '</div>'
        +   '<section class="confirmation" id="mensagem-confirmacao" role="status" aria-live="polite" hidden>'
        +       '<strong>Decisão confirmada</strong>'
        +       '<p>Opção escolhida: <span id="decisao-confirmada"></span>.</p>'
        +   '</section>'
        + '</article>';

    appState.selectedDecision = null;
    EventLogger.logTaskStarted(task.task_id);
}

function selectDecision(decision) {
    var currentTask = appState.tasks[appState.currentTaskIndex];

    if (appState.selectedDecision && appState.selectedDecision !== decision) {
        EventLogger.logDecisionChanged(currentTask.task_id, appState.selectedDecision, decision);
    } else {
        EventLogger.logDecisionMade(currentTask.task_id, decision);
    }

    appState.selectedDecision = decision;

    var btns = document.querySelectorAll('[data-decision-btn]');
    for (var i = 0; i < btns.length; i++) {
        btns[i].setAttribute('aria-pressed', 'false');
    }

    var buttonMap = {
        'approve': 'btn_approve',
        'request_adjustments': 'btn_adjust',
        'reject': 'btn_reject'
    };
    document.getElementById(buttonMap[decision]).setAttribute('aria-pressed', 'true');

    var btnConfirm = document.getElementById('btn_confirm');
    btnConfirm.disabled = false;
    btnConfirm.removeAttribute('aria-disabled');
    btnConfirm.classList.add('is-ready'); // Entrada da seta
    document.getElementById('mensagem-confirmacao').hidden = true;
}

function confirmDecision() {
    if (!appState.selectedDecision) return;

    var currentTask = appState.tasks[appState.currentTaskIndex];
    EventLogger.logTaskCompleted(currentTask.task_id);

    var btnConfirm = document.getElementById('btn_confirm');
    var seta = document.getElementById('seta');
    var ok = document.getElementById('ok');
    var btns = document.querySelectorAll('[data-decision-btn]');

    // Muda o ícone para sucesso e desabilita novas escolhas
    seta.hidden = true;
    ok.hidden = false;
    btnConfirm.classList.add('is-success');
    btnConfirm.disabled = true;
    btns.forEach(function(b) { b.disabled = true; });

    var labels = {
        'approve': 'Aprovar',
        'request_adjustments': 'Solicitar Ajustes',
        'reject': 'Rejeitar'
    };

    document.getElementById('decisao-confirmada').textContent =
        labels[appState.selectedDecision] || appState.selectedDecision;
    document.getElementById('mensagem-confirmacao').hidden = false;

    // Transição sincronizada de 1500ms para leitura do feedback
    setTimeout(function() {
        appState.currentTaskIndex++;

        if (appState.currentTaskIndex < appState.tasks.length) {
            renderTask();
        } else {
            document.getElementById('task-container').innerHTML =
                '<div class="card"><p>Obrigado por participar do experimento.</p></div>';
            EventLogger.logSessionEnd();
        }
    }, 1500);
}
