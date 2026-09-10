-- schema.sql
-- Modelo relacional do projeto de BI sobre anime.
-- load.py (carga no Supabase ou em qualquer Postgres via DATABASE_URL).

CREATE TABLE IF NOT EXISTS dim_anime (
    anime_id           INTEGER PRIMARY KEY,
    titulo             TEXT,
    tipo               TEXT,
    estudio_principal  TEXT,
    ano                INTEGER,
    temporada          TEXT,
    episodios          TEXT,
    fonte              TEXT,
    score_medio        NUMERIC,
    membros            INTEGER,
    popularidade       INTEGER
);

CREATE TABLE IF NOT EXISTS dim_genero (
    genero_id  INTEGER PRIMARY KEY,
    nome       TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS ponte_anime_genero (
    anime_id   INTEGER REFERENCES dim_anime(anime_id),
    genero_id  INTEGER REFERENCES dim_genero(genero_id),
    PRIMARY KEY (anime_id, genero_id)
);

CREATE TABLE IF NOT EXISTS fato_avaliacao (
    avaliacao_id  INTEGER PRIMARY KEY,
    anime_id      INTEGER REFERENCES dim_anime(anime_id),
    usuario_id    INTEGER,
    score         INTEGER
);
