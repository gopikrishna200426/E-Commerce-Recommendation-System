# models/content_based.py
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedModel:
    def __init__(self, text_fields, max_features=5000):
        self.text_fields = text_fields
        self.max_features = max_features
        self.vectorizer = None
        self.matrix = None  # TF-IDF sparse matrix
        self.product_ids = None

    def _combine_text(self, products: pd.DataFrame) -> pd.Series:
        texts = []
        for _, row in products.iterrows():
            parts = [str(row.get(col, "")) for col in self.text_fields]
            texts.append(" ".join(parts))
        return pd.Series(texts, index=products.index)

    def fit(self, products: pd.DataFrame):
        combo = self._combine_text(products)
        self.vectorizer = TfidfVectorizer(max_features=self.max_features, stop_words="english")
        self.matrix = self.vectorizer.fit_transform(combo)
        self.product_ids = products["product_id"].tolist()
        return self

    def recommend_similar(self, product_id: int, top_n=10, exclude_self=True):
        if self.matrix is None:
            raise ValueError("Model not fit.")
        try:
            idx = self.product_ids.index(product_id)
        except ValueError:
            return []
        sims = cosine_similarity(self.matrix[idx], self.matrix).flatten()
        order = np.argsort(-sims)
        recs = []
        for i in order:
            pid = self.product_ids[i]
            if exclude_self and pid == product_id:
                continue
            recs.append((pid, float(sims[i])))
            if len(recs) >= top_n:
                break
        return recs

    def similarity_vector(self, product_ids_list):
        idxs = [self.product_ids.index(pid) for pid in product_ids_list if pid in self.product_ids]
        if not idxs:
            return np.zeros(self.matrix.shape[0])
        sub = self.matrix[idxs]
        sims = cosine_similarity(sub, self.matrix)  
        mean_sims = np.asarray(sims).mean(axis=0)
        return mean_sims
