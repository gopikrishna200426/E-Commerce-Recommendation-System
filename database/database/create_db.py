import argparse
from pathlib import Path
from sqlalchemy import text

from db_utils import get_engine


def create_db(schema_path: str, db_uri: str):
    engine = get_engine(db_uri)
    schema_sql = Path(schema_path).read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(schema_sql))
    print(f"Database created at {db_uri}.")


def main():
    parser = argparse.ArgumentParser(description="Create DB from schema.sql")
    parser.add_argument("--schema", default="database/schema.sql")
    parser.add_argument("--db-uri", default="sqlite:///database/ecommerce.db")
    args = parser.parse_args()
    create_db(args.schema, args.db_uri)


if __name__ == "__main__":
    main()
