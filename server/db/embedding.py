from models.iic_gte_multilingual.scripts.gte_embedding import GTEEmbeddidng
from typing import Dict, List, Tuple


class EmbeddingSingletonClass(object):
    instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance') or cls.instance is None:
            cls.instance = super(EmbeddingSingletonClass, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.model = GTEEmbeddidng('G:\\CLionProjects\\aistory\\models\\iic_gte_multilingual', device="cuda") # FIXME: cuda

    def encode(self,
               texts: list[str] | None,
               dimension: int = None,
               max_length: int = 8192,
               batch_size: int = 16,
               return_dense: bool = True,
               return_sparse: bool = False):
        return self.model.encode(texts, dimension, max_length, batch_size, return_dense, return_sparse)

    def compute_scores(self,
                       text_pairs: List[Tuple[str, str]],
                       dimension: int = None,
                       max_length: int = 1024,
                       batch_size: int = 16,
                       dense_weight=1.0,
                       sparse_weight=0.1):
        return self.model.compute_scores(text_pairs, dimension, max_length, batch_size, dense_weight, sparse_weight)

class Embedding(EmbeddingSingletonClass):
    pass


if __name__ == '__main__':
  embedding = Embedding()

  query = "中国的首都在哪儿"

  docs = [
      "what is the capital of China?",
      "how to implement quick sort in python?",
      "北京",
      "快排算法介绍"
  ]

  embs = embedding.encode(docs, dimension=768, return_dense=True, return_sparse=True)
  print('dense_embeddings vecs', embs['dense_embeddings'])
  print('token_weights', embs['token_weights'])

  pairs = [(query, doc) for doc in docs]
  dense_scores = embedding.compute_scores(pairs, dense_weight=0.0, sparse_weight=1.0)
  sparse_scores = embedding.compute_scores(pairs, dense_weight=0.0, sparse_weight=1.0)
  hybird_scores = embedding.compute_scores(pairs, dense_weight=1.0, sparse_weight=0.3)

  print('dense_scores', dense_scores)
  print('sparse_scores', sparse_scores)
  print('hybird_scores', hybird_scores)
