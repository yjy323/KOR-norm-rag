import logging
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


class SentenceTransformersEmbedding:
    """
    SentenceTransformer 기반 텍스트 임베딩 클래스

    sentence-transformers 라이브러리를 사용하여 텍스트를 벡터로 변환합니다.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        device: str = "cpu",
    ):
        """
        SentenceTransformer 임베딩 초기화

        Args:
            model_name: 사용할 sentence-transformers 모델명
            device: 실행 장치 ("cpu" 또는 "cuda")
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._embedding_dim = None

        self._load_model()

    def _load_model(self) -> None:
        """임베딩 모델을 로드합니다."""
        try:
            logging.info(f"임베딩 모델 로딩 중: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self._embedding_dim = self.model.get_sentence_embedding_dimension()
            logging.info(f"모델 로딩 완료. 임베딩 차원: {self._embedding_dim}")
        except Exception as e:
            logging.error(f"모델 로딩 실패: {e}")
            raise

    def get_embedding_dim(self) -> int:
        """
        임베딩 벡터의 차원을 반환합니다.

        Returns:
            임베딩 벡터 차원수
        """
        return self._embedding_dim

    def embed_text(self, text: str) -> np.ndarray:
        """
        단일 텍스트를 임베딩 벡터로 변환합니다.

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (numpy array)
        """
        if not text or not text.strip():
            raise ValueError("입력 텍스트가 비어있습니다.")

        # 기본 텍스트 전처리
        cleaned_text = self._preprocess_text(text)

        # 임베딩 생성
        embedding = self.model.encode(cleaned_text, convert_to_numpy=True)

        return embedding

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        여러 텍스트를 배치로 임베딩 벡터로 변환합니다.

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            임베딩 벡터 배열 (shape: [len(texts), embedding_dim])
        """
        if not texts:
            raise ValueError("입력 텍스트 리스트가 비어있습니다.")

        # 빈 텍스트 검증
        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise ValueError(f"인덱스 {i}의 텍스트가 비어있습니다.")

        # 배치 텍스트 전처리
        cleaned_texts = [self._preprocess_text(text) for text in texts]

        # 배치 임베딩 생성
        embeddings = self.model.encode(
            cleaned_texts, convert_to_numpy=True, show_progress_bar=True
        )

        return embeddings

    def embed_chunks(self, chunks: List[dict]) -> np.ndarray:
        """
        청크 리스트를 임베딩 벡터로 변환합니다.

        Args:
            chunks: 청크 딕셔너리 리스트 (각 청크는 'content' 키를 포함해야 함)

        Returns:
            임베딩 벡터 배열 (shape: [len(chunks), embedding_dim])
        """
        if not chunks:
            raise ValueError("청크 리스트가 비어있습니다.")

        # 청크에서 content 추출
        texts = []
        for i, chunk in enumerate(chunks):
            if "content" not in chunk:
                raise ValueError(f"인덱스 {i}의 청크에 'content' 키가 없습니다.")
            texts.append(chunk["content"])

        return self.embed_texts(texts)

    def embed_query(self, query: str) -> np.ndarray:
        """
        검색 쿼리를 임베딩 벡터로 변환합니다.

        Args:
            query: 검색 쿼리 텍스트

        Returns:
            임베딩 벡터 (numpy array)
        """
        return self.embed_text(query)

    def _preprocess_text(self, text: str) -> str:
        """
        텍스트 전처리를 수행합니다.

        Args:
            text: 원본 텍스트

        Returns:
            전처리된 텍스트
        """
        import re

        # 기본 정리
        text = text.strip()

        # 연속된 공백을 단일 공백으로 변환
        text = re.sub(r"\s+", " ", text)

        # 연속된 줄바꿈을 단일 공백으로 변환
        text = re.sub(r"\n+", " ", text)

        return text

    def get_model_info(self) -> dict:
        """
        모델 정보를 반환합니다.

        Returns:
            모델 정보 딕셔너리
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "embedding_dim": self._embedding_dim,
            "max_seq_length": getattr(self.model, "max_seq_length", None),
        }
