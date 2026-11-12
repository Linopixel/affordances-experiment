# Guia de Execução Local

Este documento fornece o passo a passo detalhado para instalar, executar e reproduzir o experimento localmente.

## 1. Pré-requisitos

Verifique se o Python 3.10+ está instalado:

    python --version

Saída esperada: `Python 3.10.x` (ou superior).

## 2. Instalação das Dependências

Na raiz do projeto, execute:

    pip install -r requirements.txt

Saída esperada: Mensagens de instalação bem-sucedida do Flask, pandas, matplotlib, seaborn e jupyter.

## 3. Iniciar o Servidor Flask

Na raiz do projeto, inicie a API e o servidor de arquivos estáticos:

    python backend/app.py

Saída esperada:

    [SERVER] Banco de dados inicializado em: /caminho/para/affordances-experiment/data/raw/experiment.db
     * Serving Flask app 'app'
     * Debug mode: on
     * Running on http://127.0.0.1:5000

Mantenha este terminal aberto.

## 4. Acessar a Interface

Abra seu navegador e acesse:

    http://127.0.0.1:5000/

(Nota: Use o mesmo host em todas as URLs. Se acessar por `127.0.0.1`, use `127.0.0.1` para todas as requisições. Não misture `localhost` e `127.0.0.1` na mesma sessão.)

## 5. Executar uma Sessão de Teste

1. Na tela de identificação, digite um ID válido (ex: `P01`) e clique em "Continuar".
2. Role o texto do TCLE e clique em "Aceito participar".
3. O sistema redirecionará para a Versão A ou B.
4. Complete as 4 tarefas (selecionar uma decisão e clicar em "Confirmar").
5. Ao final da 4ª tarefa, aguarde o redirecionamento automático para a segunda condição.
6. Complete as 4 tarefas da segunda condição.
7. Ao final, a tela "Experimento Concluído" será exibida.

## 6. Rodar o Pipeline de Processamento

Abra um novo terminal na raiz do projeto e execute:

    python processing/run_all.py

Saída esperada:

    ==================================================
    INICIANDO PIPELINE DE PROCESSAMENTO DE DADOS
    ==================================================

    [1/4] Exportando dados brutos do SQLite...
    [EXPORT] ✅ Concluído.
      - Eventos exportados: X
      - Participantes únicos: Y
      - Sessões únicas: Z

    [2/4] Derivando erros com base na configuração experimental...
    [DERIVE] ✅ Concluído.

    [3/4] Computando métricas descritivas...
    [METRICS] ✅ Concluído.

    [4/4] Gerando comparação por participante (within-subject)...
    [PER_PARTICIPANT] ✅ Concluído.

    ==================================================
    PIPELINE CONCLUÍDO COM SUCESSO.
    ==================================================

## 7. Executar o Notebook de Análise

Antes de abrir o notebook, gere-o a partir do script auxiliar:

    python notebooks/generate_notebook.py

Isso cria o arquivo `notebooks/analysis.ipynb`. Em seguida, abra o Jupyter:

    jupyter notebook notebooks/analysis.ipynb

O navegador abrirá o notebook. No menu superior, selecione `Kernel > Restart & Run All`. Aguarde a execução de todas as células.

## 8. Onde Encontrar os Resultados

- Banco de dados bruto: `data/raw/experiment.db`
- Eventos brutos (CSV): `data/raw/raw_events.csv`
- Erros derivados: `data/processed/derived_errors.csv`
- Métricas processadas: `data/processed/processed_metrics.csv` e `data/processed/processed_metrics_summary.csv`
- Figuras para o TCC: `data/processed/figures/` (arquivos `.png`)

## 9. Como Limpar Dados de Teste

Para reiniciar o experimento com um banco de dados limpo:

1. Pare o servidor Flask (`Ctrl+C` no terminal).
2. Exclua os arquivos gerados:

No macOS/Linux:

    rm data/raw/experiment.db data/raw/raw_events.csv
    rm -rf data/processed/*

No Windows (PowerShell):

    Remove-Item data\raw\experiment.db
    Remove-Item data\raw\raw_events.csv
    Remove-Item -Recurse data\processed\*

3. Reinicie o servidor Flask (o arquivo `experiment.db` será recriado automaticamente).
