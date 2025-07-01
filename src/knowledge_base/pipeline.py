"""
Knowledge Base Pipeline
PDF 문서 로딩 -> 청킹 -> 벡터 저장소 생성까지의 전체 파이프라인
"""

import logging
import os
from typing import List, Optional

from langchain_core.documents import Document

from .chunking.kor_chunker import KORChunker
from .embedding.sentence_transformers_embedding import SentenceTransformersEmbedding
from .loading.pdf_loader import PDFLoader
from .storage.faiss_vector_store import FAISSVectorStore


class KORPipeline:
    """
    Korean RAG Pipeline

    PDF 로딩 -> 청킹 -> 임베딩 -> 벡터 저장소 저장
    """

    def __init__(self, embedding_model: SentenceTransformersEmbedding):
        """
        파이프라인 초기화

        Args:
            embedding_model: 임베딩 모델 인스턴스
        """
        self.embedding_model = embedding_model
        self.vector_store = FAISSVectorStore(self.embedding_model)

    def process_pdf(
        self, pdf_path: str, document_name: Optional[str] = None
    ) -> List[Document]:
        """
        PDF 파일을 처리하여 청크를 생성합니다.

        Args:
            pdf_path: PDF 파일 경로
            document_name: 문서명 (기본값: 파일명)

        Returns:
            생성된 청크 리스트
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

        # 문서명 설정
        if document_name is None:
            document_name = os.path.basename(pdf_path)

        logging.info(f"PDF 로딩 시작: {pdf_path}")

        # 1. PDF 로딩
        loader = PDFLoader(pdf_path)
        documents = loader.load()
        logging.info(f"로딩된 페이지 수: {len(documents)}")

        # 2. 청킹
        chunker = KORChunker(documents, document_name)
        chunks = chunker.process()
        logging.info(f"생성된 청크 수: {len(chunks)}")

        return chunks

    def build_knowledge_base(
        self, pdf_path: str, save_path: str, document_name: Optional[str] = None
    ) -> None:
        """
        PDF에서 Knowledge Base를 구축하고 저장합니다.

        Args:
            pdf_path: PDF 파일 경로
            save_path: 저장할 디렉토리 경로
            document_name: 문서명 (기본값: 파일명)
        """
        logging.info("Knowledge Base 구축 시작")

        # 1. PDF 처리 (로딩 + 청킹)
        chunks = self.process_pdf(pdf_path, document_name)

        # 2. 벡터 저장소에 추가
        logging.info("벡터 저장소에 청크 추가 중...")
        self.vector_store.add_documents(chunks)

        # 3. 로컬 저장
        logging.info(f"Knowledge Base 저장 중: {save_path}")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        self.vector_store.save(save_path)

        logging.info("Knowledge Base 구축 완료")


def main():
    """메인 실행 함수"""
    import sys

    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 파일 경로 설정
    pdf_path = "data/국어 지식 기반 생성(RAG) 참조 문서.pdf"
    save_path = "data/knowledge_base/korean_rag_reference"
    document_name = "국어_지식_기반_생성_RAG_참조_문서"

    try:
        # 임베딩 모델 초기화
        logging.info("임베딩 모델 초기화")
        embedding_model = SentenceTransformersEmbedding(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            device="cpu",
        )

        # 파이프라인 초기화
        logging.info("Knowledge Base Pipeline 초기화")
        pipeline = KORPipeline(embedding_model)

        # Knowledge Base 구축
        logging.info(f"PDF 처리 시작: {pdf_path}")
        pipeline.build_knowledge_base(
            pdf_path=pdf_path, save_path=save_path, document_name=document_name
        )

        logging.info(f"✅ Knowledge Base 구축 완료: {save_path}")

    except Exception as e:
        logging.error(f"❌ Knowledge Base 구축 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
