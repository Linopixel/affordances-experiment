# notebooks/generate_notebook.py
import json
import os

def md_cell(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip().split("\n")}

def code_cell(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.strip().split("\n")}

cells = []

cells.append(md_cell("""# Análise Descritiva — Instrumento Experimental de Avaliação de Interfaces

**TCC:** "Affordances e Significantes como Estratégias para Aprimoramento da Usabilidade e do Desempenho em Sistemas de Informação"

**Objetivo:** Apresentar indicadores comportamentais observáveis comparando a Versão A (Experimental) e a Versão B (Controle).

**Observações metodológicas:**
- Análise estritamente **descritiva**, sem testes inferenciais.
- Dados consumidos de `data/processed/`.
- Nenhum indicador é interpretado como carga cognitiva.
- Verbos usados: "observou-se", "sugere", "indica"."""),

code_cell("""import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 12

CORES = {'A': '#2B6CB0', 'B': '#4A5568'}

PROCESSED_DIR = os.path.join('..', 'data', 'processed')
RAW_DIR = os.path.join('..', 'data', 'raw')
FIGURES_DIR = os.path.join(PROCESSED_DIR, 'figures')

os.makedirs(FIGURES_DIR, exist_ok=True)

%matplotlib inline

print("Setup concluído.")"""),

code_cell("""df_metrics = pd.read_csv(os.path.join(PROCESSED_DIR, 'processed_metrics.csv'))
df_summary = pd.read_csv(os.path.join(PROCESSED_DIR, 'processed_metrics_summary.csv'))
df_errors = pd.read_csv(os.path.join(PROCESSED_DIR, 'derived_errors.csv'))
df_raw = pd.read_csv(os.path.join(RAW_DIR, 'raw_events.csv'))
df_raw['timestamp_dt'] = pd.to_datetime(df_raw['timestamp'])

print("Arquivos carregados:")
print("  - processed_metrics.csv: " + str(len(df_metrics)) + " linhas")
print("  - processed_metrics_summary.csv: " + str(len(df_summary)) + " linhas")
print("  - derived_errors.csv: " + str(len(df_errors)) + " linhas")
print("  - raw_events.csv: " + str(len(df_raw)) + " linhas")"""),

md_cell("""## 1. Caracterização da Amostra"""),

code_cell("""n_participantes = df_errors['participant_id'].nunique()
n_sessoes = df_errors['session_id'].nunique()
dist_ordem = df_errors.groupby('condition_order')['participant_id'].nunique().reset_index()
dist_ordem.columns = ['condition_order', 'n_participantes']

print("Participantes únicos: " + str(n_participantes))
print("Sessões únicas: " + str(n_sessoes))
print()
display(dist_ordem)"""),

md_cell("""## 2. Métrica 1 — Taxa de Sucesso"""),

code_cell("""display(df_summary[['condition', 'n_participantes', 'taxa_sucesso']])

display(df_metrics[['condition', 'task_id', 'taxa_sucesso']].pivot(
    index='task_id', columns='condition', values='taxa_sucesso'
).reset_index())"""),

code_cell("""fig, axes = plt.subplots(1, 2, figsize=(12, 5))

geral = df_summary[['condition', 'taxa_sucesso']]
bars1 = axes[0].bar(geral['condition'], geral['taxa_sucesso'],
                    color=[CORES[c] for c in geral['condition']])
axes[0].set_title('Taxa de Sucesso Geral por Condição')
axes[0].set_xlabel('Condição')
axes[0].set_ylabel('Taxa de Sucesso')
axes[0].set_ylim(0, 1.15)
axes[0].bar_label(bars1, fmt='%.2f', padding=3, fontsize=10)

pivot = df_metrics[['condition', 'task_id', 'taxa_sucesso']].pivot(
    index='task_id', columns='condition', values='taxa_sucesso'
)
ax2 = pivot.plot(kind='bar', ax=axes[1], color=[CORES['A'], CORES['B']], ylim=(0, 1.15))
axes[1].set_title('Taxa de Sucesso por Tarefa e Condição')
axes[1].set_xlabel('Tarefa')
axes[1].set_ylabel('Taxa de Sucesso')
axes[1].legend(title='Condição')
axes[1].tick_params(axis='x', rotation=0)
for container in ax2.containers:
    ax2.bar_label(container, fmt='%.2f', padding=3, fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'sucesso_por_condicao.png'), dpi=150, bbox_inches='tight')
plt.show()"""),

md_cell("""## 3. Métrica 2 — Tempo de Execução"""),

code_cell("""display(df_summary[['condition', 'tempo_medio_ms', 'tempo_mediano_ms']].rename(columns={
    'tempo_medio_ms': 'Tempo médio (ms)',
    'tempo_mediano_ms': 'Tempo mediano (ms)'
}))

display(df_metrics[['condition', 'task_id', 'tempo_medio_ms', 'tempo_mediano_ms',
                    'tempo_min_ms', 'tempo_max_ms', 'tempo_desvio_padrao_ms']])"""),

code_cell("""task_starts = df_raw[df_raw['event_type'] == 'task_started'][['session_id', 'task_id', 'condition', 'timestamp_dt']]
task_ends = df_raw[df_raw['event_type'] == 'task_completed'][['session_id', 'task_id', 'condition', 'timestamp_dt']]

durations_viz = pd.merge(
    task_starts, task_ends,
    on=['session_id', 'task_id', 'condition'],
    suffixes=('_start', '_end')
)
durations_viz['duration_ms'] = (durations_viz['timestamp_dt_end'] - durations_viz['timestamp_dt_start']).dt.total_seconds() * 1000

plt.figure(figsize=(8, 5))
sns.boxplot(data=durations_viz, x='condition', y='duration_ms',
            palette=[CORES['A'], CORES['B']], order=['A', 'B'])
plt.title('Distribuição do Tempo de Execução por Condição')
plt.xlabel('Condição')
plt.ylabel('Duração da Tarefa (ms)')
plt.savefig(os.path.join(FIGURES_DIR, 'tempo_boxplot.png'), dpi=150, bbox_inches='tight')
plt.show()"""),

code_cell("""pivot_tempo = df_metrics[['condition', 'task_id', 'tempo_medio_ms']].pivot(
    index='task_id', columns='condition', values='tempo_medio_ms'
)

plt.figure(figsize=(10, 5))
pivot_tempo.plot(kind='bar', color=[CORES['A'], CORES['B']])
plt.title('Tempo Médio de Execução por Tarefa e Condição')
plt.xlabel('Tarefa')
plt.ylabel('Tempo Médio (ms)')
plt.legend(title='Condição')
plt.tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'tempo_por_tarefa.png'), dpi=150, bbox_inches='tight')
plt.show()"""),

md_cell("""## 4. Métrica 3 — Erros por Tipo

- **Erro de decisão:** decisão final diferente da esperada.
- **Erro de navegação:** clique em elemento fora dos alvos válidos.
- **Omissão de ação requerida:** aplicável apenas à Versão B (ex.: não clicar em "Ver detalhes" em T03). Em A, o alerta é visível por design, então a métrica é sempre 0."""),

code_cell("""tabela_erros = df_summary[['condition', 'n_erros_decisao', 'n_erros_navegacao', 'n_erros_omissao']].copy()
tabela_erros = tabela_erros.rename(columns={
    'n_erros_decisao': 'Decisão',
    'n_erros_navegacao': 'Navegação',
    'n_erros_omissao': 'Omissão'
}).set_index('condition')
display(tabela_erros)

ax = tabela_erros.plot(kind='bar', figsize=(9, 5),
                       color=['#C53030', '#B7791F', '#4A5568'],
                       rot=0)
ax.set_title('Erros por Tipo e Condição')
ax.set_xlabel('Condição')
ax.set_ylabel('Quantidade de Erros')
ax.legend(title='Tipo de Erro', loc='upper right')
for container in ax.containers:
    ax.bar_label(container, fmt='%d', padding=3, fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'erros_por_tipo.png'), dpi=150, bbox_inches='tight')
plt.show()"""),

md_cell("""## 4.1 Acesso à informação crítica em B (T03)

Em T03 da Versão B, o alerta de justificativa ausente está escondido dentro do disclosure "Ver detalhes". A métrica abaixo registra quantos participantes **clicaram** no disclosure antes de decidir, e quantos decidiram sem acessar a informação crítica.

Este indicador **não é comparável** com A, pois em A o alerta é visível por design. Ele descreve exclusivamente o comportamento na Versão B."""),

code_cell("""df_b_t03 = df_raw[
    (df_raw['condition'] == 'B') &
    (df_raw['task_id'] == 'T03')
]

participantes_b = sorted(df_b_t03['participant_id'].unique())
linhas = []
for pid in participantes_b:
    ev = df_b_t03[df_b_t03['participant_id'] == pid]
    clicou = (
        (ev['event_type'] == 'click') &
        (ev['element_id'] == 'btn_disclosure')
    ).any()
    linhas.append({
        'participant_id': pid,
        'acessou_disclosure': 'Sim' if clicou else 'Não'
    })

df_acesso = pd.DataFrame(linhas)
display(df_acesso)

n_sim = (df_acesso['acessou_disclosure'] == 'Sim').sum()
n_total = len(df_acesso)
if n_total > 0:
    print("Participantes que clicaram no disclosure: " + str(n_sim) + " de " + str(n_total))
else:
    print("Sem dados de Versão B em T03.")"""),

md_cell("""## 5. Métricas Secundárias"""),

code_cell("""display(df_summary[['condition', 'n_interacoes_total', 'n_alteracoes_decisao', 'tempo_medio_hover_ms']])

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].bar(df_summary['condition'], df_summary['n_interacoes_total'],
            color=[CORES[c] for c in df_summary['condition']])
axes[0].set_title('Total de Interações (Cliques)')
axes[0].set_xlabel('Condição')
axes[0].set_ylabel('Quantidade')

axes[1].bar(df_summary['condition'], df_summary['n_alteracoes_decisao'],
            color=[CORES[c] for c in df_summary['condition']])
axes[1].set_title('Alterações de Decisão')
axes[1].set_xlabel('Condição')
axes[1].set_ylabel('Quantidade')

axes[2].bar(df_summary['condition'], df_summary['tempo_medio_hover_ms'],
            color=[CORES[c] for c in df_summary['condition']])
axes[2].set_title('Tempo Médio de Hover (ms)')
axes[2].set_xlabel('Condição')
axes[2].set_ylabel('Tempo (ms)')

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'metricas_secundarias.png'), dpi=150, bbox_inches='tight')
plt.show()"""),

md_cell("""## 6. Discussão dos Resultados

> **Atenção:** template de leitura. Os valores devem ser preenchidos pelo pesquisador após a coleta real.

A taxa de sucesso na Versão A foi de **[X]**, enquanto na Versão B foi de **[Y]**. A diferença sugere que a aplicação sistemática de affordances e significantes pode estar associada a decisões mais precisas.

O tempo médio de execução foi de **[X] ms** em A e **[Y] ms** em B. A diferença sugere que a organização modular e a hierarquia visual podem ter facilitado a escaneabilidade.

Em relação aos erros de navegação, a Versão B apresentou **[X]** erros a mais que a Versão A, o que pode indicar que a ausência de hierarquia visual nos botões de decisão contribuiu para cliques em elementos fora do esperado.

Em T03 da Versão B, **[X] de [Y]** participantes clicaram no disclosure "Ver detalhes" antes de decidir. Os demais decidiram sem acessar a informação crítica sobre justificativa ausente. Esse indicador descreve exclusivamente o comportamento em B, pois em A o alerta é visível por design.

**Limitações:**
- Amostra pequena e de natureza exploratória.
- Sem testes de hipótese inferenciais.
- Os resultados não permitem afirmações de causalidade.
- A ordem de apresentação das condições (AB vs BA) pode ter introduzido efeitos de aprendizagem ou fadiga."""),

md_cell("""## 7. Análise por Participante (Within-Subject)"""),

code_cell("""df_pc = pd.read_csv(os.path.join(PROCESSED_DIR, 'per_participant.csv'))

colunas_exibir = [
    'participant_id',
    'taxa_sucesso_A', 'taxa_sucesso_B', 'delta_taxa_sucesso', 'melhorou_em_sucesso',
    'tempo_medio_A_ms', 'tempo_medio_B_ms', 'delta_tempo_ms',
    'erros_total_A', 'erros_total_B', 'delta_erros_total'
]
display(df_pc[colunas_exibir])"""),

code_cell("""df_pc_sorted = df_pc.sort_values('participant_id').reset_index(drop=True)
x = range(len(df_pc_sorted))
largura = 0.35

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].bar([i - largura/2 for i in x], df_pc_sorted['taxa_sucesso_A'],
            width=largura, color=CORES['A'], label='A (Experimental)')
axes[0].bar([i + largura/2 for i in x], df_pc_sorted['taxa_sucesso_B'],
            width=largura, color=CORES['B'], label='B (Controle)')
axes[0].set_xticks(list(x))
axes[0].set_xticklabels(df_pc_sorted['participant_id'])
axes[0].set_title('Taxa de Sucesso por Participante')
axes[0].set_xlabel('Participante')
axes[0].set_ylabel('Taxa de Sucesso')
axes[0].set_ylim(0, 1.15)
axes[0].legend(loc='lower right')

axes[1].bar([i - largura/2 for i in x], df_pc_sorted['tempo_medio_A_ms'],
            width=largura, color=CORES['A'], label='A (Experimental)')
axes[1].bar([i + largura/2 for i in x], df_pc_sorted['tempo_medio_B_ms'],
            width=largura, color=CORES['B'], label='B (Controle)')
axes[1].set_xticks(list(x))
axes[1].set_xticklabels(df_pc_sorted['participant_id'])
axes[1].set_title('Tempo Médio por Participante')
axes[1].set_xlabel('Participante')
axes[1].set_ylabel('Tempo médio (ms)')
axes[1].legend(loc='upper right')

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'within_subject_por_participante.png'),
            dpi=150, bbox_inches='tight')
plt.show()"""),

md_cell("""### 7.1 Leitura por participante

> Template de leitura. Valores preenchidos pelo pesquisador após a coleta real.

Para cada participante, comparou-se o desempenho entre as duas condições. Observou-se que **[X]** participantes tiveram taxa de sucesso igual ou superior em A, **[Y]** em B, e **[Z]** empataram.

Esse padrão **[reforça / relativiza]** a leitura agregada, pois o efeito observado nas médias gerais **[é consistente / está concentrado em poucos participantes]**.

Quanto ao tempo, **[X]** participantes foram mais rápidos em A e **[Y]** em B.

**Nota:** como o desenho é within-subject, a comparação por participante é a unidade de análise mais natural para este experimento.""")

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "cells": cells
}

for cell in notebook["cells"]:
    src = cell["source"]
    cell["source"] = [line + "\n" for line in src[:-1]] + [src[-1]]

output_path = os.path.join(os.path.dirname(__file__), 'analysis.ipynb')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=2)

print("Notebook gerado em: " + output_path)
