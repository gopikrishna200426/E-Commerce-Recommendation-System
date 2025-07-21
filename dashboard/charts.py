# dashboard/charts.py
import pandas as pd
import plotly.express as px


def category_pie(history_df: pd.DataFrame):
    if history_df.empty:
        return None
    counts = history_df["category"].value_counts().reset_index()
    counts.columns = ["category","count"]
    fig = px.pie(counts, names="category", values="count", title="Purchase by Category")
    return fig


def top_products_bar(transactions_df: pd.DataFrame, products_df: pd.DataFrame, top_n=10):
    counts = transactions_df.groupby("product_id")["quantity"].sum().reset_index()
    counts = counts.merge(products_df[["product_id","product_name"]], on="product_id", how="left")
    counts = counts.sort_values("quantity", ascending=False).head(top_n)
    fig = px.bar(counts, x="product_name", y="quantity", title=f"Top {top_n} Products", text="quantity")
    fig.update_layout(xaxis_tickangle=-45)
    return fig
