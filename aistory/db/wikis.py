import torch

from aistory.db.embedding import Embedding
from aistory.db.safe_transactions import safe_transactions


def _get_wiki(cursor, wiki_name):
    cursor.execute('''SELECT description FROM "WikiTable" WHERE name = %s''', (wiki_name,))
    return cursor.fetchone()[0]


def get_wiki(wiki_name):
    return safe_transactions(f"getting wiki of {wiki_name}", lambda cursor: _get_wiki(cursor, wiki_name))


def _get_useful_wikis(cursor, embedding, description: str = None, desc_embedding: torch.Tensor = None):
    if desc_embedding is None:
        assert not description is None
        desc_embedding = embedding.encode([description], 768, return_dense=True)['dense_embeddings'][0]

        # desc_embedding should be normalized, so we can calculate cosine similarity simply by inner-product two vectors.
    # For inner product, multiply by -1 (since <#> returns the negative inner product).
    cursor.execute(
        '''SELECT name, description, (desc_embedding <#> %s::vector) * -1 AS similarity FROM "WikiTable" ORDER BY similarity DESC LIMIT 4''',
        (desc_embedding.tolist(),))
    res = cursor.fetchall()
    # print(res)
    return res


def get_useful_wikis(description: str = None, desc_embedding: torch.Tensor = None, embedding=Embedding()):
    return safe_transactions(f"getting wiki of '''{description}'''",
                             lambda cursor: _get_useful_wikis(cursor, embedding, description, desc_embedding))


def _get_bool_str(b: bool) -> 'str':
    return 'TRUE' if b else 'FALSE'

