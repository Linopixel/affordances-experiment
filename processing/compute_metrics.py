# processing/compute_metrics.py
import pandas as pd
import os

def compute_metrics():
    raw_csv = os.path.join('data', 'raw', 'raw_events.csv')
    errors_csv = os.path.join('data', 'processed', 'derived_errors.csv')
    metrics_csv = os.path.join('data', 'processed', 'processed_metrics.csv')
    summary_csv = os.path.join('data', 'processed', 'processed_metrics_summary.csv')
    
    os.makedirs(os.path.dirname(metrics_csv), exist_ok=True)
    
    df_raw = pd.read_csv(raw_csv)
    df_errors = pd.read_csv(errors_csv)
    
    df_raw['timestamp_dt'] = pd.to_datetime(df_raw['timestamp'])
    
    metrics_list = []
    
    for (cond, t_id), group_errors in df_errors.groupby(['condition', 'task_id']):
        n_tasks = len(group_errors)
        n_participantes = group_errors['participant_id'].nunique()
        
        taxa_sucesso = 1 - (group_errors['error_decision'].sum() / n_tasks) if n_tasks > 0 else 0.0
        
        task_starts = df_raw[(df_raw['event_type'] == 'task_started') & (df_raw['task_id'] == t_id) & (df_raw['condition'] == cond)]
        task_ends = df_raw[(df_raw['event_type'] == 'task_completed') & (df_raw['task_id'] == t_id) & (df_raw['condition'] == cond)]
        
        durations = pd.merge(
            task_starts[['session_id', 'task_id', 'timestamp_dt']],
            task_ends[['session_id', 'task_id', 'timestamp_dt']],
            on=['session_id', 'task_id'],
            suffixes=('_start', '_end')
        )
        durations['duration_ms'] = (durations['timestamp_dt_end'] - durations['timestamp_dt_start']).dt.total_seconds() * 1000
        
        if len(durations) > 0:
            tempo_medio_ms = durations['duration_ms'].mean()
            tempo_mediano_ms = durations['duration_ms'].median()
            tempo_min_ms = durations['duration_ms'].min()
            tempo_max_ms = durations['duration_ms'].max()
            tempo_desvio_padrao_ms = durations['duration_ms'].std()
        else:
            tempo_medio_ms = tempo_mediano_ms = tempo_min_ms = tempo_max_ms = tempo_desvio_padrao_ms = 0.0
            
        n_erros_decisao = group_errors['error_decision'].sum()
        n_erros_navegacao = group_errors['error_navigation'].sum()
        n_erros_omissao = group_errors['error_omission'].sum()
        
        group_raw = df_raw[(df_raw['condition'] == cond) & (df_raw['task_id'] == t_id)]
        n_interacoes_total = len(group_raw[group_raw['event_type'] == 'click'])
        n_alteracoes_decisao = len(group_raw[group_raw['event_type'] == 'decision_changed'])
        
        hovers = group_raw[group_raw['event_type'].isin(['hover_enter', 'hover_leave'])].copy()
        hovers = hovers.sort_values(['session_id', 'task_id', 'element_id', 'timestamp_dt'])
        
        hover_durations = []
        for (s_id, tid, elem), h_group in hovers.groupby(['session_id', 'task_id', 'element_id']):
            enters = h_group[h_group['event_type'] == 'hover_enter']['timestamp_dt']
            leaves = h_group[h_group['event_type'] == 'hover_leave']['timestamp_dt']
            for e_time in enters:
                future_leaves = leaves[leaves > e_time]
                if len(future_leaves) > 0:
                    l_time = future_leaves.iloc[0]
                    hover_durations.append((l_time - e_time).total_seconds() * 1000)
                    
        tempo_medio_hover_ms = sum(hover_durations) / len(hover_durations) if len(hover_durations) > 0 else 0.0
        
        metrics_list.append({
            'condition': cond,
            'task_id': t_id,
            'n_participantes': n_participantes,
            'taxa_sucesso': round(taxa_sucesso, 4),
            'tempo_medio_ms': round(tempo_medio_ms, 2),
            'tempo_mediano_ms': round(tempo_mediano_ms, 2),
            'tempo_min_ms': round(tempo_min_ms, 2),
            'tempo_max_ms': round(tempo_max_ms, 2),
            'tempo_desvio_padrao_ms': round(tempo_desvio_padrao_ms, 2),
            'n_erros_decisao': int(n_erros_decisao),
            'n_erros_navegacao': int(n_erros_navegacao),
            'n_erros_omissao': int(n_erros_omissao),
            'n_interacoes_total': int(n_interacoes_total),
            'n_alteracoes_decisao': int(n_alteracoes_decisao),
            'tempo_medio_hover_ms': round(tempo_medio_hover_ms, 2)
        })
        
    df_metrics = pd.DataFrame(metrics_list)
    df_metrics.to_csv(metrics_csv, index=False, encoding='utf-8')
    
    n_part_real = df_errors.groupby('condition')['participant_id'].nunique().reset_index()
    n_part_real.columns = ['condition', 'n_participantes']
    
    taxa_global = df_errors.groupby('condition').agg(
        taxa_sucesso=('error_decision', lambda x: 1 - (x.sum() / len(x)) if len(x) > 0 else 0.0)
    ).reset_index()
    
    task_starts_all = df_raw[df_raw['event_type'] == 'task_started']
    task_ends_all = df_raw[df_raw['event_type'] == 'task_completed']
    
    durations_global = pd.merge(
        task_starts_all[['session_id', 'task_id', 'condition', 'timestamp_dt']],
        task_ends_all[['session_id', 'task_id', 'condition', 'timestamp_dt']],
        on=['session_id', 'task_id', 'condition'],
        suffixes=('_start', '_end')
    )
    durations_global['duration_ms'] = (durations_global['timestamp_dt_end'] - durations_global['timestamp_dt_start']).dt.total_seconds() * 1000
    
    tempo_stats_global = durations_global.groupby('condition')['duration_ms'].agg(
        tempo_medio_ms='mean',
        tempo_mediano_ms='median'
    ).reset_index()
    
    sums_global = df_errors.groupby('condition').agg(
        n_erros_decisao=('error_decision', 'sum'),
        n_erros_navegacao=('error_navigation', 'sum'),
        n_erros_omissao=('error_omission', 'sum')
    ).reset_index()
    
    interactions_global = df_raw.groupby(['condition', 'event_type']).size().unstack(fill_value=0).reset_index()
    for col in ['click', 'decision_changed']:
        if col not in interactions_global.columns:
            interactions_global[col] = 0
    interactions_global = interactions_global[['condition', 'click', 'decision_changed']]
    interactions_global.columns = ['condition', 'n_interacoes_total', 'n_alteracoes_decisao']
    
    hovers_all = df_raw[df_raw['event_type'].isin(['hover_enter', 'hover_leave'])].copy()
    hovers_all = hovers_all.sort_values(['session_id', 'task_id', 'condition', 'element_id', 'timestamp_dt'])
    
    hover_durations_global = []
    for (s_id, tid, cond, elem), h_group in hovers_all.groupby(['session_id', 'task_id', 'condition', 'element_id']):
        enters = h_group[h_group['event_type'] == 'hover_enter']['timestamp_dt']
        leaves = h_group[h_group['event_type'] == 'hover_leave']['timestamp_dt']
        for e_time in enters:
            future_leaves = leaves[leaves > e_time]
            if len(future_leaves) > 0:
                l_time = future_leaves.iloc[0]
                hover_durations_global.append({'condition': cond, 'duration': (l_time - e_time).total_seconds() * 1000})
                
    df_hovers = pd.DataFrame(hover_durations_global)
    if not df_hovers.empty:
        tempo_medio_hover_global = df_hovers.groupby('condition')['duration'].mean().reset_index()
        tempo_medio_hover_global.columns = ['condition', 'tempo_medio_hover_ms']
    else:
        tempo_medio_hover_global = pd.DataFrame({'condition': df_errors['condition'].unique(), 'tempo_medio_hover_ms': 0.0})
    
    df_summary = n_part_real.merge(taxa_global, on='condition') \
                            .merge(tempo_stats_global, on='condition') \
                            .merge(sums_global, on='condition') \
                            .merge(interactions_global, on='condition') \
                            .merge(tempo_medio_hover_global, on='condition')
    
    cols_to_round = ['taxa_sucesso', 'tempo_medio_ms', 'tempo_mediano_ms', 
                     'n_erros_decisao', 'n_erros_navegacao', 'n_erros_omissao', 
                     'n_interacoes_total', 'n_alteracoes_decisao', 'tempo_medio_hover_ms']
    for col in cols_to_round:
        if col in df_summary.columns:
            df_summary[col] = df_summary[col].round(2)
            
    df_summary.to_csv(summary_csv, index=False, encoding='utf-8')
    
    print(f"[METRICS] ✅ Concluído.")
    print(f"  - Métricas detalhadas salvas em: {metrics_csv}")
    print(f"  - Resumo global A vs B salvo em: {summary_csv}")

if __name__ == '__main__':
    compute_metrics()
