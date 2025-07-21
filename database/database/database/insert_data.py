import argparse
import os
import pandas as pd
from sqlalchemy import text

from db_utils import get_engine


def load_schema(engine, schema_path: str):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    with engine.begin() as conn:
        conn.execute(text(schema_sql))


def load_csvs(engine, data_dir: str):
    customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    products = pd.read_csv(os.path.join(data_dir, "products.csv"))
    transactions = pd.read_csv(os.path.join(data_dir, "transactions.csv"))

    customers.to_sql("customers", engine, if_exists="append", index=False)
    products.to_sql("products", engine, if_exists="append", index=False)
    transactions.to_sql("transactions", engine, if_exists="append", index=False)


def main():
    parser = argparse.ArgumentParser(description="Load CSV data into DB.")
    parser.add_argument("--db-uri", default="sqlite:///database/ecommerce.db", help="SQLAlchemy DB URI")
    parser.add_argument("--data-dir", default="data", help="Directory containing CSV files")
    parser.add_argument("--schema", default="database/schema.sql", help="Path to schema SQL")
    args = parser.parse_args()

    engine = get_engine(args.db_uri)

    load_schema(engine, args.schema)
    load_csvs(engine, args.data_dir)
    print("Data load complete.")


if __name__ == "__main__":
    main()
