from typing import List

import faiss
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from ..embedding.sentence_transformers_embedding import SentenceTransformersEmbedding


class FAISSVectorStore:
    """
    FAISS 기반 벡터 저장소

    SentenceTransformersEmbedding과 연동하여 문서를 저장하고 관리합니다.
    """

    def __init__(self, embedding_model: SentenceTransformersEmbedding):
        """
        FAISS 벡터 저장소 초기화

        Args:
            embedding_model: SentenceTransformersEmbedding 인스턴스
        """
        self.embedding_model = embedding_model
        dimension_size = embedding_model.get_embedding_dim()

        self.db = FAISS(
            embedding_function=embedding_model,
            index=faiss.IndexFlatL2(dimension_size),
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

    def add_documents(self, documents: List[Document]) -> None:
        """
        문서를 저장소에 추가합니다.

        Args:
            documents: 저장할 문서 리스트
        """
        self.db.add_documents(documents)

    def save(self, path: str) -> None:
        """
        벡터 저장소를 로컬 파일에 저장합니다.

        Args:
            path: 저장할 디렉토리 경로
        """
        self.db.save_local(path)

    def load(self, path: str) -> None:
        """
        저장된 벡터 저장소를 로드합니다.

        Args:
            path: 로드할 디렉토리 경로
        """
        self.db = FAISS.load_local(
            path,
            embeddings=self.embedding_model,
            allow_dangerous_deserialization=True,
        )
