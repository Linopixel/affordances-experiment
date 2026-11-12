# Instrumento Experimental de Avaliação de Interfaces

Este repositório contém a aplicação web, a infraestrutura de coleta de eventos e os scripts de processamento e análise estatística desenvolvidos para o Trabalho de Conclusão de Curso (TCC) em Tecnologias e Sistemas de Informação (UFABC), intitulado: **"Affordances e Significantes como Estratégias para Aprimoramento da Usabilidade e do Desempenho em Sistemas de Informação"**.

O artefato consiste em um instrumento experimental controlado para avaliação de usabilidade em tarefas de tomada de decisão, comparando duas condições de interface (Versão A — Experimental e Versão B — Controle) em delineamento intra-sujeito (*within-subject*) com amostra de $N=20$ participantes.

---

## Estrutura do Projeto

```text
affordances-experiment/
├── backend/                # API Flask e camada de persistência SQLite
├── config/                 # Configurações do experimento (4 tarefas, regras e contrabalanceamento P01–P20)
├── data/                   # Dados brutos (raw) e bases analíticas processadas (processed)
├── docs/                   # Documentação operacional de execução e troubleshooting
├── notebooks/              # Jupyter Notebook para análise descritiva e visualização gráfica
├── processing/             # Scripts Python de consolidação, exportação, derivação de erros e métricas
├── scripts/                # Lógica JavaScript (base, logger resiliente, controle de sessão, derivações A e B)
├── styles/                 # Folhas de estilo CSS (tokens, base, derivações A e B, sessão)
├── index.html              # Ponto de entrada (identificação do participante e aceite do TCLE)
├── a.html                  # Interface da Versão A (Experimental — significantes estruturados)
├── b.html                  # Interface da Versão B (Controle — sinalização visual neutra)
└── requirements.txt        # Dependências Python do projeto
```

---

## Requisitos

* **Python:** 3.10 ou superior.
* **Navegador:** Google Chrome, Mozilla Firefox ou Microsoft Edge (versões atualizadas).
* **Sistema Operacional:** Windows, macOS ou Linux.
* **Resolução de Tela:** Mínimo de `1024px` de largura (*viewport* desktop obrigatório; dispositivos móveis são bloqueados automaticamente).

---

## Instalação

1. Clone ou baixe este repositório para sua máquina local.
2. Abra o terminal na raiz do projeto (`affordances-experiment/`).
3. *(Recomendado)* Crie e ative um ambiente virtual Python:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
4. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

---

## Execução Rápida

Para executar o ambiente experimental e reproduzir o pipeline de análise a partir da raiz do projeto:

1. **Iniciar o servidor local (porta 5000):**
   ```bash
   python backend/app.py
   ```
2. **Consolidar bancos individuais das sessões *(quando aplicável)*:**
   ```bash
   python consolidate_backups.py
   ```
3. **Executar o pipeline de processamento e derivação de métricas:**
   ```bash
   python processing/run_all.py
   ```
4. **Abrir o notebook de análise descritiva e visualização:**
   ```bash
   jupyter notebook notebooks/analysis.ipynb
   ```

---

## Fluxo do Experimento

1. O participante acessa a URL local (`http://127.0.0.1:5000`) e informa o identificador atribuído (`P01` a `P20`).
2. Realiza a leitura e o aceite formal do Termo de Consentimento Livre e Esclarecido (TCLE).
3. O sistema registra os eventos `consent_accepted` e `session_start`, consultando `config/participants.json` (`condition_order`) para direcionar automaticamente o participante à primeira condição (Grupo AB: 10 participantes; Grupo BA: 10 participantes).
4. O participante executa 4 tarefas sequenciais de aprovação de solicitações internas (`REQ-001` a `REQ-004`) em um fluxo de decisão em duas etapas (seleção da ação + acionamento do botão `Confirmar`).
5. Ao concluir a 4ª tarefa da primeira condição, o sistema redireciona automaticamente para a segunda condição experimental.
6. Ao finalizar a 4ª tarefa da segunda condição, o experimento é encerrado e o evento `session_end` é persistido no banco de dados.

---

## Pipeline de Dados e Visualização

1. **Coleta:** O *frontend* captura eventos brutos de interação (`click`, `hover`, movimentação, tempo de retenção e decisões) e os envia via `POST /event` para a API Flask com mecanismo de *retry* resiliente.
2. **Persistência:** A API grava os registros imutáveis no banco SQLite (`data/raw/experiment.db`) utilizando a restrição `INSERT OR IGNORE` por `event_id` único para impedir duplicações.
3. **Consolidação e Processamento:** Os bancos individuais de cada sessão (`experiment_ID_DATA_HORA.db`) são unificados na base consolidada (`data/raw/experiment.db`). Em seguida, `processing/run_all.py` extrai `raw_events.csv`, deriva erros operacionais (decisão, navegação e omissão) com base em `config/experiment.json` e calcula indicadores pareados em `data/processed/`.
4. **Análise Gráfica:** O notebook `notebooks/analysis.ipynb` consome os CSVs processados para gerar as visualizações descritivas em `data/processed/figures/`, incluindo a taxa de sucesso por tarefa, distribuição de tempos em segundos com escala logarítmica (`tempo_boxplot.png`), distribuição de erros, métricas de micro-interação e comparação intra-sujeito empilhada (`within_subject_por_participante.png`).

---

## Documentação Adicional

Para instruções detalhadas de condução presencial, arquitetura e solução de problemas, consulte:

- [Protocolo de Coleta Presencial](docs/COLETA.md)
- [Guia de Execução Local](docs/EXECUCAO.md)
- [Solução de Problemas (Troubleshooting)](docs/TROUBLESHOOTING.md)

---

## Licença e Uso Acadêmico

Este projeto foi desenvolvido exclusivamente para fins acadêmicos e de pesquisa científica no âmbito da Universidade Federal do ABC (UFABC). Os dados coletados são anonimizados e tratados em conformidade com a Lei Geral de Proteção de Dados (LGPD — Lei nº 13.709/2018), sem armazenar qualquer informação pessoal identificável.