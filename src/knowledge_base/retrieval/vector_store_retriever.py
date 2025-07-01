"""
Vector Store Retriever
구축된 벡터 DB에서 검색 쿼리를 수행하는 모듈
"""

import logging
import os
from typing import List, Optional

from langchain_core.documents import Document

from ..embedding.sentence_transformers_embedding import SentenceTransformersEmbedding
from ..storage.faiss_vector_store import FAISSVectorStore


class VectorStoreRetriever:
    """
    벡터 저장소 기반 검색기

    저장된 벡터 DB를 로드하고 검색 쿼리를 수행
    """

    def __init__(
        self, vector_store_path: str, embedding_model: SentenceTransformersEmbedding
    ):
        """
        검색기 초기화

        Args:
            vector_store_path: 벡터 저장소 경로
            embedding_model: 임베딩 모델 인스턴스
        """
        self.vector_store_path = vector_store_path
        self.embedding_model = embedding_model

        # 벡터 저장소 초기화 및 로드
        self.vector_store = FAISSVectorStore(self.embedding_model)
        self._load_vector_store()

    def _load_vector_store(self) -> None:
        """벡터 저장소를 로드합니다."""
        faiss_file = os.path.join(self.vector_store_path, "index.faiss")
        if not os.path.exists(faiss_file):
            raise FileNotFoundError(
                f"벡터 저장소를 찾을 수 없습니다: {self.vector_store_path}"
            )

        logging.info(f"벡터 저장소 로딩 중: {self.vector_store_path}")
        self.vector_store.load(self.vector_store_path)
        logging.info("벡터 저장소 로딩 완료")

    def search(
        self, query: str, k: int = 5, score_threshold: Optional[float] = None
    ) -> List[Document]:
        """
        검색 쿼리를 수행합니다.

        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
            score_threshold: 최소 유사도 점수 (선택사항)

        Returns:
            검색된 문서 리스트
        """
        logging.info(f"검색 쿼리: '{query}' (k={k})")

        if score_threshold is not None:
            # 점수 기반 검색
            results = self.vector_store.db.similarity_search_with_score(query, k=k)
            filtered_results = [
                doc for doc, score in results if score >= score_threshold
            ]
            logging.info(
                f"검색 결과: {len(filtered_results)}개 (점수 임계값: {score_threshold})"
            )
            return filtered_results
        else:
            # 일반 검색
            results = self.vector_store.db.similarity_search(query, k=k)
            logging.info(f"검색 결과: {len(results)}개")
            return results

    def search_with_scores(
        self, query: str, k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        검색 쿼리를 수행하고 유사도 점수를 함께 반환합니다.

        Args:
            query: 검색 쿼리
            k: 반환할 문서 수

        Returns:
            (문서, 유사도 점수) 튜플 리스트
        """
        logging.info(f"점수 포함 검색 쿼리: '{query}' (k={k})")
        results = self.vector_store.db.similarity_search_with_score(query, k=k)
        logging.info(f"검색 결과: {len(results)}개")
        return results

    def get_relevant_documents(
        self, query: str, k: int = 5, min_score: float = 0.0
    ) -> List[Document]:
        """
        관련성 높은 문서들을 검색합니다.

        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
            min_score: 최소 관련성 점수

        Returns:
            관련성 높은 문서 리스트
        """
        results_with_scores = self.vector_store.db.similarity_search_with_score(
            query, k=k
        )

        relevant_docs = []
        for doc, score in results_with_scores:
            if score >= min_score:
                # 메타데이터에 점수 추가
                doc.metadata["similarity_score"] = score
                relevant_docs.append(doc)

        logging.info(
            f"관련성 높은 문서: {len(relevant_docs)}개 (최소 점수: {min_score})"
        )
        return relevant_docs
