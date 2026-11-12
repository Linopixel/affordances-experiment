# Guia Operacional para Condução da Coleta Presencial

Este documento estabelece o protocolo padrão para a condução das sessões experimentais presenciais. O rigor na aplicação deste roteiro é fundamental para garantir a validade interna do experimento e evitar a contaminação dos dados por viés do pesquisador.

## 1. Contexto

A coleta será realizada de forma **presencial**, com o participante sentado no iMac do próprio pesquisador. O sistema experimental roda localmente, acessado via `http://127.0.0.1:5000/`. Cada participante executará **ambas as condições** (Versão A e Versão B) no mesmo dispositivo, na mesma sessão, com a ordem contrabalanceada automaticamente pelo sistema.

## 2. Checklist Pré-Sessão

Antes de cada participante chegar, o pesquisador deve verificar rigorosamente os seguintes itens:

- [ ] O servidor Flask está rodando no terminal (`python backend/app.py`).
- [ ] O navegador está aberto e apontando estritamente para `http://127.0.0.1:5000/` (evitar `localhost` para manter consistência absoluta).
- [ ] A janela do navegador está maximizada (garantindo viewport ≥ 1024px).
- [ ] O zoom do navegador está em 100% (`Ctrl+0` ou `Cmd+0`).
- [ ] As notificações do sistema operacional (macOS) estão silenciadas (Modo "Não Perturbe").
- [ ] Outros programas estão fechados (manter apenas o navegador e o terminal do Flask).
- [ ] O TCLE está disponível (impresso para assinatura ou pronto para leitura na tela, conforme exigência do comitê de ética).
- [ ] O ID do participante a ser testado foi consultado previamente em `config/participants.json`.
- [ ] Não há arquivo `experiment.db` residual de uma sessão anterior em `data/raw/` (se houver, ele deve ser movido para a pasta de backups).

## 3. Roteiro de Condução

Siga esta sequência exata de ações e falas durante a sessão:

1. **Recepção:** Receba o participante, ofereça água e explique brevemente que ele testará um sistema de aprovação de solicitações. **Não revele a hipótese do TCC** nem mencione que existem "duas versões diferentes" com objetivos de usabilidade.
2. **Duração:** Informe que a sessão dura aproximadamente 10 a 15 minutos.
3. **Consentimento:** Confirme o consentimento verbal. Se houver TCLE físico, recolha a assinatura neste momento.
4. **Início:** Peça que o participante digite o ID fornecido (ex: "P01") na tela inicial e clique em "Continuar".
5. **TCLE na tela:** Deixe que o participante leia o termo na tela e clique em "Aceito participar" por conta própria.
6. **Execução:** A partir do momento em que a primeira tarefa aparecer, **o pesquisador deve cessar qualquer interação verbal**.
7. **Postura:** Não olhe fixamente para a tela do participante. Volte-se para suas anotações ou para o terminal do Flask (sem comentar o que vê).
8. **Anotações:** Registre apenas **observações factuais e comportamentais** em uma folha à parte. Exemplos válidos: "hesitou por 5 segundos antes de clicar", "moveu o mouse em círculos sobre o botão", "murmurou 'onde está o valor?'". Exemplos inválidos (interpretações): "ficou confuso", "não entendeu o design".
9. **Encerramento:** Ao final da segunda condição, quando a tela "Experimento Concluído" aparecer, agradeça a participação e finalize a sessão.

**Regra de Ouro:** O pesquisador **não deve** dar dicas, não deve apontar elementos na tela, não deve comentar sobre o design, não deve corrigir decisões do participante e não deve demonstrar surpresa ou concordância facial/verbal. Toda interferência contamina a variável dependente.

## 4. O que NÃO Fazer

- **NÃO** comente sobre as diferenças visuais entre a primeira e a segunda parte do teste.
- **NÃO** pergunte "o que você achou?" ou "foi difícil?" durante a execução das tarefas (isso pertence exclusivamente ao questionário pós-teste, se aplicável).
- **NÃO** aponte para a tela com o dedo ou com o mouse.
- **NÃO** corrija o participante se ele clicar no botão errado (o erro é um dado valioso).
- **NÃO** interrompa o fluxo com perguntas, a menos que haja uma falha técnica crítica (ex: travamento do navegador).

## 5. Encerramento e Backup (Obrigatório)

Imediatamente após o participante sair e a tela de conclusão ser exibida:

1. Verifique no terminal do Flask se a mensagem `[SERVER] ✅ Evento persistido: session_end` foi registrada.
2. Pare o servidor Flask pressionando `Ctrl+C` no terminal.
3. Copie o arquivo `data/raw/experiment.db` para a pasta de backups, renomeando-o com o padrão `experiment_<ID>_<AAAAMMDD_HHMM>.db` (exemplo: `experiment_P01_20261009_1430.db`).
4. Abra (ou crie) o arquivo `data/raw/backups/log.csv` e adicione uma linha com: `participant_id, data_hora_inicio, data_hora_fim, observacoes` (exemplo: `P01, 2026-10-09 14:15, 2026-10-09 14:28, "Hesitou na T03, leu a justificativa duas vezes"`).
5. **Apague** o arquivo original `data/raw/experiment.db` para garantir que a próxima sessão comece com um banco limpo.
6. Reinicie o servidor Flask (`python backend/app.py`) para o próximo participante.

## 6. Consolidação de Múltiplos Bancos

Após a conclusão de todas as sessões de coleta, os dados estarão fragmentados em vários arquivos na pasta `data/raw/backups/`. Para análise, eles devem ser unificados.

1. Execute o script de consolidação na raiz do projeto:

       python processing/consolidate_backups.py

2. O script criará um arquivo `data/raw/consolidated.db` contendo todos os eventos de todos os backups.
3. Renomeie `consolidated.db` para `experiment.db` (ou ajuste o pipeline para ler o consolidado).
4. Execute o pipeline de processamento normalmente:

       python processing/run_all.py

## 7. Nota sobre Deploy Público

> **Nota metodológica:** O deploy público do sistema em ambiente remoto (hospedagem na nuvem) está **fora do escopo** deste MVP. A coleta presencial, com o sistema rodando localmente no equipamento do pesquisador, atende integralmente aos requisitos metodológicos do TCC, garantindo controle total sobre variáveis de ambiente (hardware, rede, viewport) e conformidade estrita com a LGPD, uma vez que os dados brutos nunca deixam a máquina local. Uma eventual extensão para coleta remota pode ser considerada em trabalho futuro, desde que acompanhada de salvaguardas adicionais (backup automático em nuvem criptografada, atualização do TCLE para coleta remota e auditoria de segurança).
