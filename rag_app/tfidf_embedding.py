import pickle
from chromadb import EmbeddingFunction, Documents, Embeddings
from sklearn.feature_extraction.text import TfidfVectorizer
import os

class TfidfEmbeddingFunction(EmbeddingFunction):
    def __init__(self, vectorizer_path: str = None, max_features: int = 384):
        self.vectorizer_path = vectorizer_path
        self.max_features = max_features
        self.vectorizer = None
        
        if vectorizer_path and os.path.exists(vectorizer_path):
            with open(vectorizer_path, "rb") as f:
                self.vectorizer = pickle.load(f)
        else:
            self.vectorizer = TfidfVectorizer(max_features=self.max_features)
            
    def fit(self, documents: Documents):
        self.vectorizer.fit(documents)
        if self.vectorizer_path:
            with open(self.vectorizer_path, "wb") as f:
                pickle.dump(self.vectorizer, f)

    def __call__(self, input: Documents) -> Embeddings:
        if not self.vectorizer:
             # Should be fit first or loaded
             raise ValueError("Vectorizer not fit or loaded.")
        # Transform and convert to list of lists (dense)
        # Force float32 for compatibility
        import numpy as np
        vectors = self.vectorizer.transform(input).astype(np.float32).toarray().tolist()
        return vectors
