#!/usr/bin/env python3
"""
VectorStoreRetriever 테스트 스크립트
구축된 벡터 DB에서 검색 기능을 테스트
"""

import logging
import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from knowledge_base.embedding.sentence_transformers_embedding import (
    SentenceTransformersEmbedding,
)
from knowledge_base.retrieval.vector_store_retriever import VectorStoreRetriever


def main():
    """메인 테스트 함수"""
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 벡터 저장소 경로
    vector_store_path = "data/knowledge_base/korean_rag_reference"

    try:
        # 임베딩 모델 초기화
        logging.info("임베딩 모델 초기화")
        embedding_model = SentenceTransformersEmbedding(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            device="cpu",
        )

        # 검색기 초기화
        logging.info("VectorStoreRetriever 초기화")
        retriever = VectorStoreRetriever(vector_store_path, embedding_model)

        # 테스트 쿼리들
        test_queries = [
            "한국어 자연어 처리",
            "문법 체계",
            "음성학적 특징",
            "어휘 분석",
            "형태소 분석",
            "구문 분석",
        ]

        print("\n" + "=" * 80)
        print("벡터 저장소 검색 테스트")
        print("=" * 80)

        for i, query in enumerate(test_queries, 1):
            print(f"\n[테스트 {i}] 쿼리: '{query}'")
            print("-" * 50)

            # 일반 검색 (상위 3개)
            results = retriever.search(query, k=3)

            for j, doc in enumerate(results, 1):
                title = doc.metadata.get("title", "Unknown")
                chunk_id = doc.metadata.get("chunk_id", "Unknown")
                content_preview = doc.page_content[:100].replace("\n", " ")

                print(f"{j}. {title} ({chunk_id})")
                print(f"   내용: {content_preview}...")
                print()

        # 점수 포함 검색 테스트
        print("\n" + "=" * 80)
        print("점수 포함 검색 테스트")
        print("=" * 80)

        test_query = "한국어 자연어 처리"
        print(f"\n쿼리: '{test_query}'")
        print("-" * 50)

        results_with_scores = retriever.search_with_scores(test_query, k=5)

        for i, (doc, score) in enumerate(results_with_scores, 1):
            title = doc.metadata.get("title", "Unknown")
            chunk_id = doc.metadata.get("chunk_id", "Unknown")
            content_preview = doc.page_content[:80].replace("\n", " ")

            print(f"{i}. 점수: {score:.4f} | {title} ({chunk_id})")
            print(f"   내용: {content_preview}...")
            print()

        # 관련성 높은 문서 검색 테스트
        print("\n" + "=" * 80)
        print("관련성 높은 문서 검색 테스트 (최소 점수: 0.5)")
        print("=" * 80)

        relevant_docs = retriever.get_relevant_documents(
            test_query, k=10, min_score=0.5
        )

        print(f"\n쿼리: '{test_query}'")
        print(f"관련성 높은 문서 수: {len(relevant_docs)}개")
        print("-" * 50)

        for i, doc in enumerate(relevant_docs, 1):
            title = doc.metadata.get("title", "Unknown")
            chunk_id = doc.metadata.get("chunk_id", "Unknown")
            score = doc.metadata.get("similarity_score", 0.0)
            content_preview = doc.page_content[:80].replace("\n", " ")

            print(f"{i}. 점수: {score:.4f} | {title} ({chunk_id})")
            print(f"   내용: {content_preview}...")
            print()

        print("\n✅ 모든 검색 테스트 완료!")

    except Exception as e:
        logging.error(f"❌ 검색 테스트 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
