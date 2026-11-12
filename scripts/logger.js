/* ==========================================================================
   LOGGER.JS - Event Logger do Instrumento Experimental
   Comum às versões Base, A e B.

   Captura só é ativa após `session_start`. `captureEnabled` é restaurado
   do sessionStorage em qualquer página nova (a/b) para persistir após o redirect.
   ========================================================================== */

const EventLogger = (function() {
    let sessionStartTime = 0;
    let currentTaskId = null;
    let isTaskActive = false;
    let lastMousePos = { x: 0, y: 0 };
    let samplingStarted = false;
    let captureEnabled = false;

    let context = {
        participant_id: "P00",
        session_id: "S00",
        condition: "A",
        condition_order: "AB"
    };

    const retryQueue = [];
    const MAX_RETRIES = 3;
    const RETRY_DELAY_MS = 3000;

    function generateUUID() {
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
            return crypto.randomUUID();
        }
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function createEvent(eventType, options) {
        options = options || {};
        const now = new Date();
        const elapsed = sessionStartTime > 0 ? (performance.now() - sessionStartTime) : 0;

        return {
            event_id: generateUUID(),
            participant_id: context.participant_id,
            session_id: context.session_id,
            condition: context.condition,
            condition_order: context.condition_order,
            task_id: options.task_id || currentTaskId || null,
            event_type: eventType,
            element_id: options.element_id || null,
            timestamp: now.toISOString(),
            server_timestamp: "",
            elapsed_ms: parseFloat(elapsed.toFixed(2)),
            x: options.x !== undefined ? options.x : null,
            y: options.y !== undefined ? options.y : null,
            metadata: options.metadata ? JSON.stringify(options.metadata) : "{}",
            retries: 0
        };
    }

    async function sendEvent(event) {
        try {
            const response = await fetch('/event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event)
            });
            if (!response.ok) {
                const errorData = await response.json().catch(function() { return {}; });
                throw new Error(errorData.error || 'Network response was not ok');
            }
            console.log('[LOGGER] OK ' + event.event_type + ' | ID: ' + event.event_id);
            return true;
        } catch (error) {
            console.warn('[LOGGER] Falha: ' + event.event_id + ' tentativa ' + (event.retries + 1));
            event.retries += 1;
            if (event.retries <= MAX_RETRIES) {
                retryQueue.push(event);
            } else {
                console.error('[LOGGER] Evento perdido: ' + event.event_id);
            }
            return false;
        }
    }

    function processRetryQueue() {
        if (retryQueue.length > 0) {
            const event = retryQueue.shift();
            sendEvent(event);
        }
        setTimeout(processRetryQueue, RETRY_DELAY_MS);
    }

    function setContext(newContext) {
        context = Object.assign({}, context, newContext);
    }

    function logEventAlways(eventType, options) {
        const event = createEvent(eventType, options);
        return sendEvent(event);
    }

    function logEvent(eventType, options) {
        if (!captureEnabled) return;
        return logEventAlways(eventType, options);
    }

    function logConsentAccepted() {
        return logEventAlways('consent_accepted');
    }

    function logSessionStart(metadata) {
        sessionStartTime = performance.now();
        sessionStorage.setItem('session_start_time', sessionStartTime.toString());
        captureEnabled = true;
        return logEventAlways('session_start', { metadata: metadata });
    }

    function stop() {
        captureEnabled = false;
        isTaskActive = false;
        if (typeof samplingStarted !== 'undefined') {
            samplingStarted = false;
        }
        console.log('[LOGGER] Rastreamento totalmente interrompido.');
    }

    function logSessionEnd() {
        isTaskActive = false;
        logEvent('session_end');
        stop();
    }

    function logTaskStarted(taskId) {
        currentTaskId = taskId;
        isTaskActive = true;
        logEvent('task_started', { task_id: taskId });
    }

    function logTaskCompleted(taskId) {
        logEvent('task_completed', { task_id: taskId });
    }

    function logDecisionMade(taskId, decision) {
        logEvent('decision_made', { task_id: taskId, metadata: { decision: decision } });
    }

    function logDecisionChanged(taskId, fromDecision, toDecision) {
        logEvent('decision_changed', { task_id: taskId, metadata: { from: fromDecision, to: toDecision } });
    }

    function setupAutomaticListeners() {
        document.addEventListener('click', function(e) {
            const target = e.target.closest('[id]');
            if (target) {
                logEvent('click', { element_id: target.id, x: e.clientX, y: e.clientY });
            }
        });

        document.addEventListener('mouseover', function(e) {
            const target = e.target.closest('[id]');
            if (!target) return;
            const related = e.relatedTarget;
            if (!related || !target.contains(related)) {
                logEvent('hover_enter', { element_id: target.id, x: e.clientX, y: e.clientY });
            }
        });

        document.addEventListener('mouseout', function(e) {
            const target = e.target.closest('[id]');
            if (!target) return;
            const related = e.relatedTarget;
            if (!related || !target.contains(related)) {
                logEvent('hover_leave', { element_id: target.id, x: e.clientX, y: e.clientY });
            }
        });

        document.addEventListener('mousemove', function(e) {
            lastMousePos = { x: e.clientX, y: e.clientY };
        });
    }

    function startMouseSampling() {
        if (samplingStarted) return;
        samplingStarted = true;
        setInterval(function() {
            if (isTaskActive) {
                logEvent('mouse_move', { x: lastMousePos.x, y: lastMousePos.y });
            }
        }, 100);
    }

    function init() {
        const saved = sessionStorage.getItem('session_start_time');
        if (saved) {
            sessionStartTime = parseFloat(saved);
            captureEnabled = true;
        }
        setupAutomaticListeners();
        startMouseSampling();
        processRetryQueue();
        console.log('[LOGGER] Inicializado. captureEnabled=' + captureEnabled);
    }

    return {
        init: init,
        setContext: setContext,
        logEvent: logEvent,
        logSessionStart: logSessionStart,
        logConsentAccepted: logConsentAccepted,
        logSessionEnd: logSessionEnd,
        stop: stop,
        logTaskStarted: logTaskStarted,
        logTaskCompleted: logTaskCompleted,
        logDecisionMade: logDecisionMade,
        logDecisionChanged: logDecisionChanged
    };
})();

document.addEventListener('DOMContentLoaded', function() {
    EventLogger.init();
});
