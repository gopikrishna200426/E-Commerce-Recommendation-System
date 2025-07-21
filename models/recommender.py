import pandas as pd

from .data_loader import DataLoader
from .content_based import ContentBasedModel
from .collaborative_filtering import CollaborativeFiltering
from .hybrid_model import HybridRecommender
from .export_reports import export_excel


class RecommenderSystem:
    def __init__(self, engine=None, config=None):
        self.engine = engine
        self.config = config or {}
        self.data = DataLoader(engine)
        self.content_model = None
        self.collab_model = None
        self.hybrid_model = None
        self.products_df = None
        self.transactions_df = None

    # ---------- Data ----------
    def load_data(self):
        self.products_df = self.data.products()
        self.transactions_df = self.data.transactions()
        return self

    # ---------- Train ----------
    def build_models(self):
        if self.products_df is None or self.transactions_df is None:
            self.load_data()
        # content
        text_fields = self.config.get("content", {}).get("text_fields", ["product_name","category","subcategory","brand","description"])
        max_features = self.config.get("content", {}).get("max_features", 5000)
        self.content_model = ContentBasedModel(text_fields=text_fields, max_features=max_features)
        self.content_model.fit(self.products_df)
        # collaborative
        min_u = self.config.get("recommender", {}).get("min_interactions_user", 1)
        min_i = self.config.get("recommender", {}).get("min_interactions_item", 1)
        self.collab_model = CollaborativeFiltering(min_u, min_i)
        interactions = self.transactions_df[["customer_id","product_id","quantity","rating"]].copy()
        self.collab_model.fit(interactions)
        # popularity
        pop = self.transactions_df.groupby("product_id")["quantity"].sum().sort_values(ascending=False)
        # hybrid
        weights = self.config.get("recommender", {}).get("weights", None)
        self.hybrid_model = HybridRecommender(self.collab_model, self.content_model, pop, weights)
        return self

    # ---------- Recommend ----------
    def get_purchase_history(self, customer_id):
        return self.data.user_history(customer_id)

    def recommend_products(self, customer_id, top_n=None):
        if self.hybrid_model is None:
            self.build_models()
        if top_n is None:
            top_n = self.config.get("recommender", {}).get("top_n", 10)
        hist = self.get_purchase_history(customer_id)
        purchased = hist["product_id"].tolist()
        recs = self.hybrid_model.recommend(customer_id, purchased, top_n=top_n)
        # decorate
        out_rows = []
        for rank, (pid, score) in enumerate(recs, start=1):
            prod = self.products_df[self.products_df.product_id == pid].iloc[0]
            out_rows.append({
                "rank": rank,
                "product_id": pid,
                "score": score,
                "product_name": prod.product_name,
                "category": prod.category,
                "subcategory": prod.subcategory,
                "brand": prod.brand,
                "price": prod.price,
            })
        return pd.DataFrame(out_rows)

    # ---------- Export ----------
    def export_all(self, outpath="data/sample_reports.xlsx", top_n=None):
        customers_df = self.data.customers()
        recs_dict = {}
        for cid in customers_df.customer_id.tolist():
            recs_dict[cid] = self.recommend_products(cid, top_n=top_n)
        export_excel(customers_df, self.products_df, self.transactions_df, recs_dict, outpath)
        return outpath
