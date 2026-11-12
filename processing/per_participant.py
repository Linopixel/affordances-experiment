# processing/per_participant.py
# Gera uma tabela comparativa A vs B por participante (análise within-subject).

import pandas as pd
import os

def compute_per_participant():
    raw_csv = os.path.join('data', 'raw', 'raw_events.csv')
    errors_csv = os.path.join('data', 'processed', 'derived_errors.csv')
    output_csv = os.path.join('data', 'processed', 'per_participant.csv')

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    df_raw = pd.read_csv(raw_csv)
    df_errors = pd.read_csv(errors_csv)
    df_raw['timestamp_dt'] = pd.to_datetime(df_raw['timestamp'])

    rows_by_pc = []
    for pid in sorted(df_errors['participant_id'].unique()):
        for cond in ['A', 'B']:
            errs = df_errors[
                (df_errors['participant_id'] == pid) &
                (df_errors['condition'] == cond)
            ]
            n_tarefas = len(errs)
            if n_tarefas == 0:
                continue

            corretas = int((errs['error_decision'] == 0).sum())
            taxa_sucesso = corretas / n_tarefas

            starts = df_raw[
                (df_raw['event_type'] == 'task_started') &
                (df_raw['participant_id'] == pid) &
                (df_raw['condition'] == cond)
            ]
            ends = df_raw[
                (df_raw['event_type'] == 'task_completed') &
                (df_raw['participant_id'] == pid) &
                (df_raw['condition'] == cond)
            ]
            durs = pd.merge(
                starts[['session_id', 'task_id', 'timestamp_dt']],
                ends[['session_id', 'task_id', 'timestamp_dt']],
                on=['session_id', 'task_id'],
                suffixes=('_start', '_end')
            )
            if len(durs) > 0:
                durs['duration_ms'] = (durs['timestamp_dt_end'] - durs['timestamp_dt_start']).dt.total_seconds() * 1000
                tempo_medio = durs['duration_ms'].mean()
            else:
                tempo_medio = 0.0

            rows_by_pc.append({
                'participant_id': pid,
                'condition': cond,
                'n_tarefas': n_tarefas,
                'decisoes_corretas': corretas,
                'taxa_sucesso': round(taxa_sucesso, 4),
                'tempo_medio_ms': round(tempo_medio, 2),
                'n_erros_total': int(errs['error_total'].sum()),
                'n_erros_decisao': int(errs['error_decision'].sum()),
                'n_erros_navegacao': int(errs['error_navigation'].sum()),
                'n_erros_omissao': int(errs['error_omission'].sum())
            })

    df_pc = pd.DataFrame(rows_by_pc)

    df_a = df_pc[df_pc['condition'] == 'A'].set_index('participant_id')
    df_b = df_pc[df_pc['condition'] == 'B'].set_index('participant_id')

    comparison = []
    for pid in sorted(df_pc['participant_id'].unique()):
        row = {'participant_id': pid}

        for cond, df_cond in [('A', df_a), ('B', df_b)]:
            if pid in df_cond.index:
                row['taxa_sucesso_' + cond] = float(df_cond.loc[pid, 'taxa_sucesso'])
                row['tempo_medio_' + cond + '_ms'] = float(df_cond.loc[pid, 'tempo_medio_ms'])
                row['erros_total_' + cond] = int(df_cond.loc[pid, 'n_erros_total'])
                row['erros_decisao_' + cond] = int(df_cond.loc[pid, 'n_erros_decisao'])
                row['erros_navegacao_' + cond] = int(df_cond.loc[pid, 'n_erros_navegacao'])
                row['erros_omissao_' + cond] = int(df_cond.loc[pid, 'n_erros_omissao'])
            else:
                row['taxa_sucesso_' + cond] = None
                row['tempo_medio_' + cond + '_ms'] = None
                row['erros_total_' + cond] = None
                row['erros_decisao_' + cond] = None
                row['erros_navegacao_' + cond] = None
                row['erros_omissao_' + cond] = None

        if row['taxa_sucesso_A'] is not None and row['taxa_sucesso_B'] is not None:
            row['delta_taxa_sucesso'] = round(row['taxa_sucesso_B'] - row['taxa_sucesso_A'], 4)
            row['delta_tempo_ms'] = round(row['tempo_medio_B_ms'] - row['tempo_medio_A_ms'], 2)
            row['delta_erros_total'] = row['erros_total_B'] - row['erros_total_A']

            if row['delta_taxa_sucesso'] > 0:
                row['melhorou_em_sucesso'] = 'B melhor'
            elif row['delta_taxa_sucesso'] < 0:
                row['melhorou_em_sucesso'] = 'A melhor'
            else:
                row['melhorou_em_sucesso'] = 'empate'
        else:
            row['delta_taxa_sucesso'] = None
            row['delta_tempo_ms'] = None
            row['delta_erros_total'] = None
            row['melhorou_em_sucesso'] = None

        comparison.append(row)

    df_comparison = pd.DataFrame(comparison)
    df_comparison.to_csv(output_csv, index=False, encoding='utf-8')

    n_participantes_completos = (
        df_comparison[['taxa_sucesso_A', 'taxa_sucesso_B']].dropna().shape[0]
    )

    print("[PER_PARTICIPANT] Concluído.")
    print("  - Participantes com A e B: " + str(n_participantes_completos))
    print("  - Arquivo salvo em: " + output_csv)

if __name__ == '__main__':
    compute_per_participant()
