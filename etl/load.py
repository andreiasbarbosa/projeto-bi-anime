"""
Cria as 4 tabelas (se ainda não existirem) e carrega os CSVs processados por transform.py no PostgreSQL. 
"""

import argparse
import os
import pandas as pd
from sqlalchemy import create_engine, text
 
# Ordem importa por causa das foreign keys (dimensões antes da tabela fato)
TABLE_LOAD_ORDER = [
    ("dim_anime.csv", "dim_anime"),
    ("dim_genero.csv", "dim_genero"),
    ("ponte_anime_genero.csv", "ponte_anime_genero"),
    ("fato_avaliacao.csv", "fato_avaliacao"),
]
 
 
def get_engine():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise EnvironmentError(
            "Defina a variável de ambiente DATABASE_URL antes de rodar o load.py "
            "(ver instruções no topo deste arquivo)."
        )
    return create_engine(database_url)
 
 
def create_schema(engine, schema_file: str):
    if not os.path.exists(schema_file):
        raise FileNotFoundError(f"Não encontrei {schema_file}.")
    with open(schema_file, "r", encoding="utf-8") as f:
        ddl = f.read()
    with engine.begin() as conn:
        conn.execute(text(ddl))
    print(f"[load] schema criado/validado a partir de {schema_file}")
 
 
def load_tables(engine, data_dir: str):
    for filename, table_name in TABLE_LOAD_ORDER:
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Não encontrei {path}. Rode transform.py antes do load.py.")
 
        df = pd.read_csv(path)
        df.to_sql(table_name, engine, if_exists="append", index=False, method="multi", chunksize=5000)
        print(f"[load] {table_name}: {len(df):,} linhas carregadas")
 
 
def main():
    parser = argparse.ArgumentParser(description="Carga das tabelas processadas no PostgreSQL")
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--schema-file", default="database/schema.sql")
    parser.add_argument("--skip-schema", action="store_true", help="Pular criação do schema (ex.: já criado via docker init)")
    args = parser.parse_args()
 
    engine = get_engine()
 
    if not args.skip_schema:
        create_schema(engine, args.schema_file)
 
    load_tables(engine, args.data_dir)
    print("[load] carga concluída com sucesso.")
 
 
if __name__ == "__main__":
    main()
