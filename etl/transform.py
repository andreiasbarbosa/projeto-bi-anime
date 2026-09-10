"""
A partir dos dados brutos (anime.csv + rating_complete.csv) e da contagem de avaliações por anime (gerado no extract.py), monta as 4 tabelas do modelo
relacional definido.

Observação importante: o rating_complete.csv não tem data da avaliação
(só user_id, anime_id, rating). Por isso o ano usado nas análises temporais vem do campo Premiered/Aired do próprio anime.csv (ano de lançamento),
e não de quando a avaliação foi feita.

"""

import argparse
import os
import re
import pandas as pd
 
from extract import load_anime_raw, count_ratings_per_anime
 
TOP_N_DEFAULT = 1000
SAMPLE_PER_ANIME_DEFAULT = 300
RATING_CHUNKSIZE = 5_000_000
 
 
def extract_year(row: pd.Series) -> "int | None":
    """Extrai o ano de lançamento a partir de Premiered (ex.: 'Spring 1998')
    e, se não existir, cai para o começo do campo Aired (ex.: 'Apr 3, 1998 to ...')."""
    premiered = str(row.get("Premiered", "Unknown"))
    m = re.search(r"(\d{4})", premiered)
    if m:
        return int(m.group(1))
 
    aired = str(row.get("Aired", ""))
    m2 = re.search(r"(\d{4})", aired)
    if m2:
        return int(m2.group(1))
 
    return None
 
 
def extract_season(row: pd.Series) -> "str | None":
    """Extrai a temporada de lançamento (Winter/Spring/Summer/Fall) a partir
    de Premiered (ex.: 'Spring 1998' -> 'Spring').
 
    O campo Premiered só é preenchido pelo MyAnimeList para animes de TV. Movies, OVAs, Specials e ONAs não têm o conceito de "temporada de
    exibição", então para esses tipos o valor retornado é None."""
    premiered = str(row.get("Premiered", "Unknown"))
    if premiered == "Unknown" or premiered.strip() == "":
        return None
    return premiered.split(" ")[0].strip()
 
TIPO_PT = {
    "TV": "TV",
    "Movie": "Filme",
    "OVA": "OVA",
    "ONA": "ONA",
    "Special": "Especial",
    "Music": "Música",
}
 
TEMPORADA_PT = {
    "Spring": "Primavera",
    "Summer": "Verão",
    "Fall": "Outono",
    "Winter": "Inverno",
}
 
FONTE_PT = {
    "Book": "Livro",
    "Game": "Jogo",
}
 
TEMPORADA_AUSENTE = "Não aplicável"
 
 
def build_dim_anime(anime_raw: pd.DataFrame, top_ids: set) -> pd.DataFrame:
    anime = anime_raw[anime_raw["MAL_ID"].isin(top_ids)].copy()
 
    anime["ano"] = anime.apply(extract_year, axis=1)
    anime["temporada"] = anime.apply(extract_season, axis=1)
    anime["estudio_principal"] = anime["Studios"].apply(
        lambda s: str(s).split(",")[0].strip() if pd.notna(s) else "Unknown"
    )
 
    dim_anime = anime[
        ["MAL_ID", "Name", "Type", "estudio_principal", "ano", "temporada", "Episodes", "Source", "Score", "Members", "Popularity"]
    ].rename(
        columns={
            "MAL_ID": "anime_id",
            "Name": "titulo",
            "Type": "tipo",
            "Episodes": "episodios",
            "Source": "fonte",
            "Score": "score_medio",
            "Members": "membros",
            "Popularity": "popularidade",
        }
    )
 
    # Traduções para português
    dim_anime["tipo"] = dim_anime["tipo"].map(TIPO_PT).fillna(dim_anime["tipo"])
    dim_anime["fonte"] = dim_anime["fonte"].map(FONTE_PT).fillna(dim_anime["fonte"])
    dim_anime["temporada"] = dim_anime["temporada"].map(TEMPORADA_PT).fillna(TEMPORADA_AUSENTE)
 
    return dim_anime, anime 
 
 
def build_genero_tables(anime_filtered: pd.DataFrame):
    genero_set = set()
    pares = []
    for _, row in anime_filtered.iterrows():
        gs = str(row["Genres"]) if pd.notna(row["Genres"]) else ""
        for g in [x.strip() for x in gs.split(",") if x.strip()]:
            genero_set.add(g)
            pares.append((row["MAL_ID"], g))
 
    generos_ordenados = sorted(genero_set)
    genero_id_map = {g: i + 1 for i, g in enumerate(generos_ordenados)}
 
    dim_genero = pd.DataFrame(
        [(gid, g) for g, gid in genero_id_map.items()], columns=["genero_id", "nome"]
    )
    ponte = pd.DataFrame(
        [(aid, genero_id_map[g]) for aid, g in pares], columns=["anime_id", "genero_id"]
    )
    return dim_genero, ponte
 
 
def build_fato_avaliacao(raw_dir: str, top_ids: set, sample_per_anime: int) -> pd.DataFrame:
    path = os.path.join(raw_dir, "rating_complete.csv")
    buffer = {aid: [] for aid in top_ids}
 
    for i, chunk in enumerate(pd.read_csv(path, chunksize=RATING_CHUNKSIZE)):
        chunk = chunk[chunk["anime_id"].isin(top_ids)]
        for aid, group in chunk.groupby("anime_id"):
            cur = buffer[aid]
            need = sample_per_anime - len(cur)
            if need > 0:
                take = group.sample(n=min(need, len(group)), random_state=42)
                cur.extend(take.to_dict("records"))
        print(f"[transform] chunk {i + 1} de ratings processado")
 
    rows = [r for lst in buffer.values() for r in lst]
    fato = pd.DataFrame(rows)
    fato.insert(0, "avaliacao_id", range(1, len(fato) + 1))
    fato = fato.rename(columns={"rating": "score", "user_id": "usuario_id"})
    return fato[["avaliacao_id", "anime_id", "usuario_id", "score"]]
 
 
def main():
    parser = argparse.ArgumentParser(description="Transformação dos dados em 4 tabelas do modelo relacional")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--out-dir", default="data/processed")
    parser.add_argument("--top-n", type=int, default=TOP_N_DEFAULT)
    parser.add_argument("--sample-per-anime", type=int, default=SAMPLE_PER_ANIME_DEFAULT)
    args = parser.parse_args()
 
    os.makedirs(args.out_dir, exist_ok=True)
 
    anime_raw = load_anime_raw(args.raw_dir)
    counts = count_ratings_per_anime(args.raw_dir)
    top_ids = set(counts.head(args.top_n).index)
    print(f"[transform] {len(top_ids)} animes selecionados (top {args.top_n} por nº de avaliações)")
 
    dim_anime, anime_filtered = build_dim_anime(anime_raw, top_ids)
    dim_anime.to_csv(os.path.join(args.out_dir, "dim_anime.csv"), index=False)
    print(f"[transform] dim_anime.csv salvo: {dim_anime.shape}")
 
    dim_genero, ponte = build_genero_tables(anime_filtered)
    dim_genero.to_csv(os.path.join(args.out_dir, "dim_genero.csv"), index=False)
    ponte.to_csv(os.path.join(args.out_dir, "ponte_anime_genero.csv"), index=False)
    print(f"[transform] dim_genero.csv salvo: {dim_genero.shape}")
    print(f"[transform] ponte_anime_genero.csv salvo: {ponte.shape}")
 
    fato = build_fato_avaliacao(args.raw_dir, top_ids, args.sample_per_anime)
    fato.to_csv(os.path.join(args.out_dir, "fato_avaliacao.csv"), index=False)
    print(f"[transform] fato_avaliacao.csv salvo: {fato.shape}")
 
 
if __name__ == "__main__":
    main()
