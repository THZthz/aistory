# aistory

Trying to make an interactive fiction world with the power of LLM.


### Stacks

- Sentence embedding - mGTE: Local deployed, details of how the model is trained can be found in this paper 
[mGTE: Generalized Long-Context Text Representation and Reranking Models for Multilingual Text Retrieval](https://arxiv.org/abs/2407.19669). Model
can be downloaded from [modelscope](https://www.modelscope.cn/models/iic/gte_sentence-embedding_multilingual-base/files).
Note that you will need to install pytorch[cuda] to run it in full speed. You should put the model under folder 
*models/iic_gte_multilingual*.
- Database - PostgreSQL.
- Server - Flask.
- Website - React.