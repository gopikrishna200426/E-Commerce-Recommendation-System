# models/collaborative_filtering.py
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFiltering:
    """Implicit item-based collaborative filtering using purchase counts (quantity) or ratings."""
    def __init__(self, min_interactions_user=1, min_interactions_item=1):
        self.min_interactions_user = min_interactions_user
        self.min_interactions_item = min_interactions_item
        self.user_index = {}
        self.item_index = {}
        self.index_user = {}
        self.index_item = {}
        self.matrix = None  # users x items CSR
        self.item_sims = None

    def _filter(self, interactions: pd.DataFrame):
        u_counts = interactions.groupby("customer_id").size()
        keep_users = u_counts[u_counts >= self.min_interactions_user].index
        i_counts = interactions.groupby("product_id").size()
        keep_items = i_counts[i_counts >= self.min_interactions_item].index
        return interactions[(interactions.customer_id.isin(keep_users)) & (interactions.product_id.isin(keep_items))]

    def fit(self, interactions: pd.DataFrame):
        # expected cols: customer_id, product_id, quantity OR rating
        df = interactions.copy()
        df = self._filter(df)

        # signal: rating if available else quantity else 1
        if "rating" in df and df["rating"].notna().any():
            signal = df["rating"].fillna(0)
        elif "quantity" in df:
            signal = df["quantity"].fillna(1)
        else:
            signal = 1.0

        users = df.customer_id.unique().tolist()
        items = df.product_id.unique().tolist()
        self.user_index = {u: i for i, u in enumerate(users)}
        self.item_index = {p: i for i, p in enumerate(items)}
        self.index_user = {i: u for u, i in self.user_index.items()}
        self.index_item = {i: p for p, i in self.item_index.items()}

        rows = df.customer_id.map(self.user_index)
        cols = df.product_id.map(self.item_index)
        data = pd.Series(signal).astype(float)
        self.matrix = csr_matrix((data, (rows, cols)), shape=(len(users), len(items)))

        # cosine similarity item-item
        self.item_sims = cosine_similarity(self.matrix.T)
        return self

    def recommend_for_user(self, customer_id: int, top_n=10, exclude_items=None):
        if self.matrix is None:
            raise ValueError("Model not fit.")
        if customer_id not in self.user_index:
            return []
        uidx = self.user_index[customer_id]
        user_vector = self.matrix[uidx]  # 1 x items
        scores = user_vector.dot(self.item_sims).A1

        # exclude purchased
        if exclude_items:
            for pid in exclude_items:
                if pid in self.item_index:
                    scores[self.item_index[pid]] = -np.inf

        order = np.argsort(-scores)
        recs = []
        for i in order:
            if len(recs) >= top_n:
                break
            if scores[i] == -np.inf:
                continue
            pid = self.index_item[i]
            recs.append((pid, float(scores[i])))
        return recs
