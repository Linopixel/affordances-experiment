# processing/run_all.py
import export_raw
import derive_errors
import compute_metrics
import per_participant

def main():
    print("=" * 50)
    print("INICIANDO PIPELINE DE PROCESSAMENTO DE DADOS")
    print("=" * 50)

    print("\n[1/4] Exportando dados brutos do SQLite...")
    export_raw.export_raw_data()

    print("\n[2/4] Derivando erros com base na configuração experimental...")
    derive_errors.derive_errors()

    print("\n[3/4] Computando métricas descritivas...")
    compute_metrics.compute_metrics()

    print("\n[4/4] Gerando comparação por participante (within-subject)...")
    per_participant.compute_per_participant()

    print("\n" + "=" * 50)
    print("PIPELINE CONCLUÍDO COM SUCESSO.")
    print("Verifique os arquivos gerados no diretório data/processed/")
    print("=" * 50)

if __name__ == '__main__':
    main()
