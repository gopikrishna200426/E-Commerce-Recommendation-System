import numpy as np
import pandas as pd


class HybridRecommender:
    """Blend collaborative, content, and popularity scores."""
    def __init__(self, collab_model, content_model, popularity_series, weights=None):
        if weights is None:
            weights = {"collaborative": 0.6, "content": 0.3, "popularity": 0.1}
        self.w = weights
        self.collab = collab_model
        self.content = content_model
        self.popularity = popularity_series  # pd.Series indexed by product_id

    def recommend(self, customer_id: int, purchased_ids, top_n=10):
        # Collaborative scores
        collab_scores = {}
        if self.collab is not None:
            for pid, score in self.collab.recommend_for_user(customer_id, top_n=100, exclude_items=purchased_ids):
                collab_scores[pid] = score

        # Content scores
        content_scores = {}
        if self.content is not None and purchased_ids:
            sims = self.content.similarity_vector(purchased_ids)
            for pid, score in zip(self.content.product_ids, sims):
                if pid in purchased_ids:
                    continue
                content_scores[pid] = float(score)

        # Popularity normalized 0..1
        pop = self.popularity.copy()
        if len(pop) > 0:
            pop = (pop - pop.min()) / (pop.max() - pop.min() + 1e-9)
        pop_scores = pop.to_dict()

        # Combine
        all_ids = set(collab_scores) | set(content_scores) | set(pop_scores)
        combined = []
        for pid in all_ids:
            c = collab_scores.get(pid, 0.0)
            t = content_scores.get(pid, 0.0)
            p = pop_scores.get(pid, 0.0)
            score = self.w["collaborative"] * c + self.w["content"] * t + self.w["popularity"] * p
            combined.append((pid, float(score)))
        combined.sort(key=lambda x: x[1], reverse=True)
        return combined[:top_n]
