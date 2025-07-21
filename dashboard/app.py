# dashboard/app.py
import streamlit as st
import pandas as pd
import yaml
from pathlib import Path

from models import RecommenderSystem
from database.db_utils import get_engine
from .charts import category_pie, top_products_bar

st.set_page_config(page_title="E-Commerce Recommender", layout="wide")


CONFIG_PATH = Path("config.yaml") if Path("config.yaml").exists() else Path("config_example.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


engine = get_engine(config["database"]["uri"])
recommender = RecommenderSystem(engine=engine, config=config)
recommender.load_data().build_models()

customers_df = recommender.data.customers()
products_df = recommender.products_df
transactions_df = recommender.transactions_df

st.title("E-Commerce Recommendation System Dashboard")


st.sidebar.header("Select Customer")
selected_customer = st.sidebar.selectbox(
    "Customer", options=customers_df.customer_id.tolist(), format_func=lambda cid: customers_df.loc[customers_df.customer_id==cid, "customer_name"].values[0]
)

st.sidebar.markdown("---")
export_btn = st.sidebar.button("Export Excel Report")


col1, col2 = st.columns([1,1])

with col1:
    st.subheader("Purchase History")
    hist = recommender.get_purchase_history(selected_customer)
    st.dataframe(hist)

with col2:
    st.subheader("Recommended Products")
    recs = recommender.recommend_products(selected_customer)
    st.dataframe(recs)

st.markdown("---")


c1, c2 = st.columns([1,1])
with c1:
    st.subheader("Category Mix")
    fig = category_pie(hist)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No purchase history.")

with c2:
    st.subheader("Top Products Overall")
    fig2 = top_products_bar(transactions_df, products_df, top_n=10)
    st.plotly_chart(fig2, use_container_width=True)


if export_btn:
    outpath = recommender.export_all(outpath=config["export"]["excel_filename"], top_n=config["recommender"]["top_n"])
    st.success(f"Report exported: {outpath}")
    st.download_button(
        label="Download Excel",
        data=open(outpath, "rb").read(),
        file_name=outpath.split("/")[-1],
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
