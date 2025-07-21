# models/data_loader.py
import pandas as pd
from sqlalchemy import text


class DataLoader:
    """Centralized data access from SQL DB into DataFrames."""
    def __init__(self, engine):
        self.engine = engine

    def customers(self) -> pd.DataFrame:
        return pd.read_sql("SELECT * FROM customers", self.engine)

    def products(self) -> pd.DataFrame:
        return pd.read_sql("SELECT * FROM products", self.engine)

    def transactions(self) -> pd.DataFrame:
        df = pd.read_sql("SELECT * FROM transactions", self.engine, parse_dates=["purchase_timestamp"])
        return df

    def user_history(self, customer_id: int) -> pd.DataFrame:
        q = text(
            """
            SELECT t.*, p.product_name, p.category, p.subcategory, p.brand, p.price
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            WHERE t.customer_id = :cid
            ORDER BY t.purchase_timestamp DESC
            """
        )
        return pd.read_sql(q, self.engine, params={"cid": customer_id}, parse_dates=["purchase_timestamp"])
