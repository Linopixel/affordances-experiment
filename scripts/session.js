/* ==========================================================================
   SESSION.JS - Controle de fluxo pré-experimental, contrabalanceamento e transição
   ========================================================================== */

const SessionManager = (function() {
    let allowNavigation = false;

    function checkViewport() {
        if (window.innerWidth < 1024) {
            const blocked = document.getElementById('blocked-screen');
            if (blocked) blocked.classList.add('active');
            const welcome = document.getElementById('welcome-screen');
            if (welcome) welcome.classList.remove('active');
            const consent = document.getElementById('consent-screen');
            if (consent) consent.classList.remove('active');
            return false;
        }
        return true;
    }

    function setupReloadGuard() {
        window.addEventListener('beforeunload', function(e) {
            if (allowNavigation) return;
            if (!sessionStorage.getItem('session_start_time')) return;
            if (sessionStorage.getItem('experiment_finished') === 'true') return;
            e.preventDefault();
            e.returnValue = '';
            return '';
        });
    }

    async function validateParticipant() {
        const inputId = document.getElementById('participant-id-input').value.trim().toUpperCase();
        const errorMsg = document.getElementById('id-error');
        const btn = document.getElementById('btn-continue-id');

        if (!inputId) {
            errorMsg.textContent = "Por favor, insira o ID do participante.";
            errorMsg.classList.add('active');
            return;
        }

        btn.disabled = true;
        btn.textContent = "Verificando...";

        try {
            const response = await fetch('config/participants.json');
            const participants = await response.json();

            if (participants[inputId]) {
                sessionStorage.setItem('participant_id', inputId);
                sessionStorage.setItem('condition_order', participants[inputId].condition_order);
                document.getElementById('welcome-screen').classList.remove('active');
                document.getElementById('consent-screen').classList.add('active');
            } else {
                errorMsg.textContent = "ID não encontrado na lista de participantes. Verifique com o pesquisador.";
                errorMsg.classList.add('active');
            }
        } catch (error) {
            errorMsg.textContent = "Erro ao carregar configuração. Recarregue a página.";
            errorMsg.classList.add('active');
            console.error(error);
        } finally {
            btn.disabled = false;
            btn.textContent = "Continuar";
        }
    }

    async function acceptConsent() {
        let sessionId = sessionStorage.getItem('session_id');
        if (!sessionId) {
            sessionId = 'S' + Date.now() + Math.random().toString(36).substr(2, 5);
            sessionStorage.setItem('session_id', sessionId);
        }

        const participantId = sessionStorage.getItem('participant_id');
        let conditionOrder = sessionStorage.getItem('condition_order');
        if (!conditionOrder || conditionOrder === 'undefined') { conditionOrder = 'AB'; }
        const currentCondition = conditionOrder.charAt(0);

        if (typeof EventLogger !== 'undefined') {
            EventLogger.setContext({
                participant_id: participantId,
                session_id: sessionId,
                condition: currentCondition,
                condition_order: conditionOrder
            });

            await EventLogger.logConsentAccepted();

            const metadata = {
                screen_width: window.screen.width,
                screen_height: window.screen.height,
                viewport_width: window.innerWidth,
                viewport_height: window.innerHeight,
                browser: navigator.userAgent,
                os: navigator.platform,
                language: navigator.language,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            };

            await EventLogger.logSessionStart(metadata);
        }

        allowNavigation = true;
        window.location.href = '/' + currentCondition.toLowerCase();
    }

    function setupTransitionObserver() {
        const taskContainer = document.getElementById('task-container');
        if (!taskContainer) return;

        const observer = new MutationObserver(function(mutations) {
            for (let i = 0; i < mutations.length; i++) {
                if (mutations[i].type === 'childList') {
                    if (taskContainer.innerHTML.includes('Obrigado por participar do experimento')) {
                        observer.disconnect();
                        handleConditionTransition();
                    }
                }
            }
        });

        observer.observe(taskContainer, { childList: true, subtree: true });
    }

    function handleConditionTransition() {
        let conditionOrder = sessionStorage.getItem('condition_order');
        if (!conditionOrder || conditionOrder === 'undefined') { conditionOrder = 'AB'; }
        const currentCondition = sessionStorage.getItem('current_condition_override') || conditionOrder.charAt(0);

        let nextCondition = '';
        if (currentCondition === 'A' && conditionOrder === 'AB') nextCondition = 'B';
        else if (currentCondition === 'B' && conditionOrder === 'BA') nextCondition = 'A';

        if (nextCondition) {
            sessionStorage.setItem('current_condition_override', nextCondition);
            setTimeout(function() {
                allowNavigation = true;
                window.location.href = '/' + nextCondition.toLowerCase();
            }, 1000);
        } else {
            sessionStorage.setItem('experiment_finished', 'true');
            if (typeof EventLogger !== 'undefined') {
                EventLogger.logSessionEnd();
            }
            document.getElementById('task-container').innerHTML =
                '<div class="card" style="text-align: center; padding: var(--spacing-xl);">' +
                '<h2 style="color: var(--color-primary);">Experimento Concluído</h2>' +
                '<p>Obrigado pela sua participação. Você pode fechar esta aba.</p>' +
                '</div>';
        }
    }

    function init() {
        if (!checkViewport()) return;
        setupReloadGuard();

        const path = window.location.pathname;
        if (path === '/a' || path === '/a.html' || path === '/b' || path === '/b.html') {
            const pId = sessionStorage.getItem('participant_id');
            const sId = sessionStorage.getItem('session_id');
            const cOrder = sessionStorage.getItem('condition_order');
            const cCond = sessionStorage.getItem('current_condition_override') || cOrder.charAt(0);

            if (pId && sId && typeof EventLogger !== 'undefined') {
                EventLogger.setContext({
                    participant_id: pId,
                    session_id: sId,
                    condition: cCond,
                    condition_order: cOrder
                });
            }
            setupTransitionObserver();
            return;
        }

        document.getElementById('welcome-screen').classList.add('active');
        document.getElementById('btn-continue-id').addEventListener('click', validateParticipant);
        document.getElementById('btn-accept-consent').addEventListener('click', acceptConsent);
    }

    return { init: init };
})();

document.addEventListener('DOMContentLoaded', SessionManager.init);
