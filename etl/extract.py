"""
Lê os dois arquivos brutos baixados do Kaggle (dataset "Anime Recommendation
Database 2020" - hernan4444) e expõe funções para:
  - carregar o anime.csv (pequeno, cabe inteiro em memória)
  - contar quantas avaliações cada anime tem no rating_complete.csv. Como é grande (~800MB / ~57M linhas) e por isso é lido em chunks.

Os arquivos brutos NÃO são versionados no Git (ver README). Baixe-os do Kaggle antes de rodar este script:
https://www.kaggle.com/hernan4444/anime-recommendation-database-2020

Uso:
    python extract.py --raw-dir data/raw --out-dir data/interim
"""

import argparse
import os
import pandas as pd

RATING_CHUNKSIZE = 5_000_000


def load_anime_raw(raw_dir: str) -> pd.DataFrame:
    """Carrega o anime.csv bruto (metadados de todos os animes do dataset)."""
    path = os.path.join(raw_dir, "anime.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Não encontrei {path}. Baixe o dataset do Kaggle e coloque o "
            f"anime.csv em {raw_dir}/ antes de rodar o ETL."
        )
    return pd.read_csv(path)


def count_ratings_per_anime(raw_dir: str, chunksize: int = RATING_CHUNKSIZE) -> pd.Series:
    """
    Percorre o rating_complete.csv em chunks (arquivo grande demais para carregar de uma vez) e retorna quantas avaliações cada anime_id tem,
    ordenado do mais avaliado para o menos avaliado.
    """
    path = os.path.join(raw_dir, "rating_complete.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Não encontrei {path}. Baixe o dataset do Kaggle e coloque o "
            f"rating_complete.csv em {raw_dir}/ antes de rodar o ETL."
        )

    counts = pd.Series(dtype="int64")
    total_rows = 0
    for i, chunk in enumerate(pd.read_csv(path, chunksize=chunksize, usecols=["anime_id"])):
        total_rows += len(chunk)
        counts = counts.add(chunk["anime_id"].value_counts(), fill_value=0)
        print(f"[extract] chunk {i + 1} processado — {total_rows:,} linhas acumuladas")

    counts = counts.astype("int64").sort_values(ascending=False)
    print(f"[extract] total de avaliações no arquivo: {total_rows:,}")
    print(f"[extract] total de animes distintos avaliados: {len(counts):,}")
    return counts


def main():
    parser = argparse.ArgumentParser(description="Extração dos dados brutos do Kaggle")
    parser.add_argument("--raw-dir", default="data/raw", help="Pasta com anime.csv e rating_complete.csv")
    parser.add_argument("--out-dir", default="data/interim", help="Pasta para salvar resultados intermediários")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    anime = load_anime_raw(args.raw_dir)
    print(f"[extract] anime.csv carregado: {anime.shape[0]:,} linhas")

    counts = count_ratings_per_anime(args.raw_dir)
    counts.to_csv(os.path.join(args.out_dir, "anime_rating_counts.csv"), header=["n_ratings"])
    print(f"[extract] contagem de avaliações por anime salva em {args.out_dir}/anime_rating_counts.csv")


if __name__ == "__main__":
    main()
