// ==========================================================================
// B.JS - Derivação B (Controle)
// Sobrescreve funções do app.js. Aplica o layout B + instrumentação.
// ==========================================================================

function renderTask() {
    var task = appState.tasks[appState.currentTaskIndex];
    if (!task) return;

    var container = document.getElementById('task-container');
    var request = task.request;

    var hasJustification = request.justification && request.justification.trim() !== '';

    container.innerHTML = ''
        + '<article class="card">'
        +   '<header class="card__header">'
        +       '<h2 class="card__id" id="request_id">' + request.request_id + '</h2>'
        +       '<span class="priority" id="priority_badge">Prioridade: ' + request.priority + '</span>'
        +   '</header>'
        +   (!hasJustification
                ? '<div class="disclosure">'
                    + '<button type="button" class="disclosure__trigger" id="btn_disclosure" aria-expanded="false" aria-controls="disclosure-content" onclick="toggleDisclosure(event)">'
                    +   '<span>Ver detalhes</span>'
                    +   '<span class="disclosure__arrow" aria-hidden="true">\u25BC</span>'
                    + '</button>'
                    + '<div class="disclosure__content" id="disclosure-content" data-open="false">'
                    +   '<div class="alert-inline">Justificativa ausente</div>'
                    + '</div>'
                  + '</div>'
                : '')
        +   '<section class="section">'
        +       '<dl>'
        +           '<div class="detail-row"><dt>Valor</dt><dd id="request_value">' + request.value + '</dd></div>'
        +           '<div class="detail-row"><dt>Impacto</dt><dd id="request_impact">' + request.impact + '</dd></div>'
        +           '<div class="detail-row"><dt>Prazo</dt><dd id="request_deadline">' + request.deadline + '</dd></div>'
        +           '<div class="detail-row"><dt>Custo</dt><dd id="request_cost">' + request.cost + '</dd></div>'
        +           '<div class="detail-row detail-row--stacked"><dt>Justificativa</dt>'
        +               '<dd id="request_justification"' + (hasJustification ? '' : ' class="is-empty"') + '>'
        +                   (hasJustification ? request.justification : '')
        +               '</dd>'
        +           '</div>'
        +           '<div class="detail-row detail-row--stacked"><dt>Histórico</dt><dd id="request_history">' + request.history + '</dd></div>'
        +       '</dl>'
        +   '</section>'
        +   '<div class="actions">'
        +       '<div class="decision-group" role="group" aria-label="Decisão" id="decisoes">'
        +           '<button type="button" class="btn" id="btn_approve" data-decision-btn aria-pressed="false" onclick="selectDecision(\'approve\')">'
        +               '<span class="check" aria-hidden="true">\u2713</span>Aprovar'
        +           '</button>'
        +           '<button type="button" class="btn" id="btn_adjust" data-decision-btn aria-pressed="false" onclick="selectDecision(\'request_adjustments\')">'
        +               '<span class="check" aria-hidden="true">\u2713</span>Solicitar Ajustes'
        +           '</button>'
        +           '<button type="button" class="btn" id="btn_reject" data-decision-btn aria-pressed="false" onclick="selectDecision(\'reject\')">'
        +               '<span class="check" aria-hidden="true">\u2713</span>Rejeitar'
        +           '</button>'
        +       '</div>'
        +       '<button type="button" class="btn btn--confirm" id="btn_confirm" onclick="confirmDecision()" disabled>Confirmar</button>'
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

    document.getElementById('btn_confirm').disabled = false;
    document.getElementById('mensagem-confirmacao').hidden = true;
}

function confirmDecision() {
    if (!appState.selectedDecision) return;

    var currentTask = appState.tasks[appState.currentTaskIndex];

    EventLogger.logTaskCompleted(currentTask.task_id);

    var labels = {
        'approve': 'Aprovar',
        'request_adjustments': 'Solicitar Ajustes',
        'reject': 'Rejeitar'
    };
    document.getElementById('decisao-confirmada').textContent =
        labels[appState.selectedDecision] || appState.selectedDecision;
    document.getElementById('mensagem-confirmacao').hidden = false;
    document.getElementById('btn_confirm').disabled = true;

    // Transição sincronizada para 1500ms (mesmo tempo total de A)
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

function toggleDisclosure(e) {
    var trigger = e.currentTarget;
    var content = trigger.nextElementSibling;
    if (!content) return;
    var isOpen = content.getAttribute('data-open') === 'true';
    content.setAttribute('data-open', isOpen ? 'false' : 'true');
    trigger.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
}
