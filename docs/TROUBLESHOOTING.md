# Solução de Problemas (Troubleshooting)

Este documento lista os problemas mais comuns durante a execução local e suas respectivas soluções.

---

## 1. Erro: Porta 5000 já em uso

- **Sintoma:** Ao executar `python backend/app.py`, o terminal exibe `OSError: [Errno 98] Address already in use` ou `Port 5000 is in use`.
- **Causa provável:** Uma instância anterior do Flask não foi encerrada corretamente ou outro serviço está usando a porta.
- **Solução:**
  - No Windows: abra o Gerenciador de Tarefas e encerre processos `python.exe`.
  - No macOS/Linux: execute `lsof -ti:5000 | xargs kill -9` no terminal.
  - Alternativamente, altere a porta no `backend/app.py` (ex: `port=5001`).

---

## 2. Erro: ModuleNotFoundError

- **Sintoma:** Ao rodar qualquer script Python, o terminal exibe `ModuleNotFoundError: No module named 'flask'` (ou pandas, seaborn, etc.).
- **Causa provável:** As dependências não foram instaladas ou o ambiente virtual ativo não é o mesmo onde foram instaladas.
- **Solução:** Certifique-se de que o ambiente virtual está ativado e execute novamente: `pip install -r requirements.txt`.

---

## 3. Eventos não chegam ao servidor (Erro de CORS ou Rede)

- **Sintoma:** O console do navegador (F12) mostra erros de rede ou CORS, e o terminal do Flask não registra `[SERVER] ✅ Evento persistido`.
- **Causa provável:** O arquivo HTML foi aberto diretamente pelo sistema de arquivos (URL começa com `file://`) ou há divergência entre `localhost` e `127.0.0.1`.
- **Solução:** Acesse a aplicação estritamente via `http://127.0.0.1:5000/` com o servidor Flask rodando.

---

## 4. Tela de bloqueio mobile aparece indevidamente

- **Sintoma:** A tela exibe "Viewport Insuficiente" mesmo em um computador.
- **Causa provável:** A janela do navegador está redimensionada com largura inferior a 1024px, ou o modo de dispositivo móvel do DevTools está ativo.
- **Solução:** Maximize a janela do navegador ou desative o modo de dispositivo móvel (ícone de celular/tablet no DevTools) e recarregue a página (F5).

---

## 5. Notebook não encontra os arquivos CSV

- **Sintoma:** Ao executar a Célula 3 do `analysis.ipynb`, ocorre `FileNotFoundError`.
- **Causa provável:** O pipeline de processamento (`run_all.py`) ainda não foi executado, ou foi executado em um diretório diferente da raiz do projeto.
- **Solução:** Na raiz do projeto, execute `python processing/run_all.py` e verifique se os arquivos aparecem na pasta `data/processed/`.

---

## 6. Evento enviado duas vezes pelo Logger (mas registrado apenas uma vez)

- **Sintoma:** O console do navegador mostra dois `[LOGGER] ✅ Confirmado` para o mesmo `event_id`, mas o banco registra apenas uma entrada.
- **Causa provável:** Isso é o comportamento esperado do mecanismo de retry. Quando o servidor não confirma o recebimento a tempo, o Logger reenvia o evento com o mesmo `event_id`. A cláusula `INSERT OR IGNORE` do SQLite ignora silenciosamente a segunda inserção, evitando duplicata.
- **Solução:** Nenhuma ação necessária. O comportamento é correto e garante resiliência sem duplicação.

---

## 7. O evento session_start não aparece no banco

- **Sintoma:** O banco registra `consent_accepted`, mas não `session_start`, ou a sessão parece começar no meio do fluxo.
- **Causa provável:** O participante avançou sem clicar formalmente no botão "Aceito participar" do TCLE, ou o navegador bloqueou o `sessionStorage`.
- **Solução:** Garanta que o fluxo seja seguido rigorosamente: Identificação → TCLE → Clique em "Aceito participar". Verifique se o navegador permite armazenamento de sessão.

---

## 8. Eventos de mouse_move não são registrados

- **Sintoma:** O console do navegador não mostra logs de `mouse_move`, ou o CSV final não contém esse tipo de evento.
- **Causa provável:** A página foi aberta via protocolo `file://` em vez de `http://`. Alguns navegadores restringem `setInterval` ou APIs de performance em arquivos locais por segurança.
- **Solução:** Certifique-se de que o servidor Flask está rodando e acesse via `http://127.0.0.1:5000/`.

---

## 9. O arquivo consolidated.db não foi gerado

- **Sintoma:** Após rodar o script de consolidação, o arquivo `data/raw/consolidated.db` não aparece.
- **Causa provável:** A pasta `data/raw/backups/` está vazia (não há arquivos `experiment_*.db` para consolidar) ou o script não encontrou nenhum arquivo com esse padrão de nome.
- **Solução:** Certifique-se de que os bancos de dados de cada participante foram movidos para a pasta `backups/` e renomeados seguindo o padrão `experiment_<ID>_<DATA>.db` (conforme o guia `COLETA.md`).


