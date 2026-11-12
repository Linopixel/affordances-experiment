# processing/derive_errors.py
import pandas as pd
import json
import os

def derive_errors():
    raw_csv = os.path.join('data', 'raw', 'raw_events.csv')
    config_path = os.path.join('config', 'experiment.json')
    output_csv = os.path.join('data', 'processed', 'derived_errors.csv')

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    df_raw = pd.read_csv(raw_csv)
    df_raw = df_raw.sort_values('timestamp').reset_index(drop=True)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    df_raw['metadata_dict'] = df_raw['metadata'].apply(
        lambda x: json.loads(x) if pd.notnull(x) and x != '{}' else {}
    )

    grouped = df_raw.groupby(
        ['participant_id', 'session_id', 'condition', 'condition_order', 'task_id']
    )

    results = []

    for (p_id, s_id, cond, c_order, t_id), group in grouped:
        if pd.isna(t_id):
            continue

        task_config = config['tasks'].get(t_id, {})
        expected_decision = task_config.get('expected_decision', '')
        valid_targets = task_config.get('valid_targets', [])
        required_actions = task_config.get('required_actions', {})
        condition_required = required_actions.get(cond, [])

        # --- Erro de decisão ---
        decision_events = group[
            group['event_type'].isin(['decision_made', 'decision_changed'])
        ].sort_values('timestamp')

        final_decision = None
        for _, ev in decision_events.iterrows():
            md = ev['metadata_dict']
            if ev['event_type'] == 'decision_made':
                final_decision = md.get('decision')
            elif ev['event_type'] == 'decision_changed':
                final_decision = md.get('to')

        if final_decision is None:
            decision = None
            error_decision = 1
        else:
            decision = final_decision
            error_decision = 1 if decision != expected_decision else 0

        # --- Erro de navegação ---
        clicks = group[group['event_type'] == 'click']
        invalid_clicks = 0
        for _, row in clicks.iterrows():
            elem = row['element_id']
            if pd.notnull(elem) and str(elem).strip() != '' and elem not in valid_targets:
                invalid_clicks += 1
        error_navigation = invalid_clicks

        # --- Omissão de ação requerida (só quando há required_actions para a condição) ---
        error_omission = 0
        if condition_required:
            clicked_elements = group[group['event_type'] == 'click']['element_id'].dropna().unique()
            missing = [req for req in condition_required if req not in clicked_elements]
            if len(missing) > 0:
                error_omission = 1

        results.append({
            'participant_id': p_id,
            'session_id': s_id,
            'condition': cond,
            'condition_order': c_order,
            'task_id': t_id,
            'decision': decision,
            'expected_decision': expected_decision,
            'error_decision': error_decision,
            'error_navigation': error_navigation,
            'error_omission': error_omission,
            'error_total': error_decision + error_navigation + error_omission
        })

    df_errors = pd.DataFrame(results)
    df_errors.to_csv(output_csv, index=False, encoding='utf-8')

    print("[DERIVE] Concluído.")
    print("  - Tarefas processadas: " + str(len(df_errors)))
    print("  - Arquivo salvo em: " + output_csv)

if __name__ == '__main__':
    derive_errors()
