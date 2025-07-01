"""
FAISSVectorStore 기능 테스트 코드
"""

from langchain_core.documents import Document

from knowledge_base.embedding.sentence_transformers_embedding import (
    SentenceTransformersEmbedding,
)
from knowledge_base.storage.faiss_vector_store import FAISSVectorStore


def test_vector_store():
    """FAISSVectorStore의 기본 기능을 테스트합니다."""

    print("1. 임베딩 모델 초기화 중...")
    embedding_model = SentenceTransformersEmbedding()
    print(f"   임베딩 차원: {embedding_model.get_embedding_dim()}")

    print("\n2. 벡터 저장소 초기화 중...")
    vector_store = FAISSVectorStore(embedding_model)

    print("\n3. 테스트 문서 생성 중...")
    test_documents = [
        Document(
            page_content="한국어 자연어 처리는 매우 중요한 분야입니다.",
            metadata={"title": "자연어 처리", "page": 1, "chunk_id": "KOR-001"},
        ),
        Document(
            page_content="머신러닝과 딥러닝은 인공지능의 핵심 기술입니다.",
            metadata={"title": "인공지능", "page": 2, "chunk_id": "KOR-002"},
        ),
        Document(
            page_content="검색 시스템에서 벡터 유사도는 중요한 역할을 합니다.",
            metadata={"title": "검색 시스템", "page": 3, "chunk_id": "KOR-003"},
        ),
    ]

    print(f"   생성된 문서 수: {len(test_documents)}")

    print("\n4. 문서를 벡터 저장소에 추가 중...")
    vector_store.add_documents(test_documents)
    print("   문서 추가 완료")

    print("\n5. 벡터 저장소 저장 중...")
    save_path = "./test_knowledge_base"
    vector_store.save(save_path)
    print(f"   저장 완료: {save_path}")

    print("\n6. 새로운 벡터 저장소로 로드 테스트...")
    new_embedding_model = SentenceTransformersEmbedding()
    new_vector_store = FAISSVectorStore(new_embedding_model)
    new_vector_store.load(save_path)
    print("   로드 완료")

    print("\n7. 유사도 검색 테스트...")
    query = "자연어 처리 기술"
    search_results = new_vector_store.db.similarity_search(query, k=2)

    print(f"   쿼리: '{query}'")
    print(f"   검색 결과 수: {len(search_results)}")

    for i, doc in enumerate(search_results, 1):
        print(f"   결과 {i}:")
        print(f"     내용: {doc.page_content}")
        print(f"     메타데이터: {doc.metadata}")
        print()

    print("✅ 모든 테스트 완료!")


def test_with_kor_chunker():
    """KORChunker와 연동하여 전체 파이프라인을 테스트합니다."""
    from knowledge_base.chunking.kor_chunker import KORChunker

    print("\n=== KORChunker 연동 테스트 ===")

    print("1. 테스트 문서 생성...")
    test_docs = [
        Document(
            page_content="""
            <제1조 목적>
            이 규정은 한국어 자연어 처리의 기본 원칙을 정한다.
            
            <제2조 정의>
            이 규정에서 사용하는 용어의 뜻은 다음과 같다.
            1. "자연어 처리"란 컴퓨터가 인간의 언어를 이해하고 처리하는 기술을 말한다.
            2. "임베딩"이란 텍스트를 벡터로 변환하는 과정을 말한다.
            
            <제3조 적용범위>
            이 규정은 모든 한국어 텍스트 처리에 적용된다.
            """,
            metadata={"source": "test_regulation.pdf", "page": 1},
        )
    ]

    print("2. KORChunker로 청킹...")
    chunker = KORChunker(test_docs, "테스트_규정")
    chunks = chunker.process()
    print(f"   생성된 청크 수: {len(chunks)}")

    for i, chunk in enumerate(chunks):
        print(f"   청크 {i+1}: {chunk.metadata['title']}")

    print("\n3. 임베딩 및 벡터 저장소 생성...")
    embedding_model = SentenceTransformersEmbedding()
    vector_store = FAISSVectorStore(embedding_model)

    print("4. 청크를 벡터 저장소에 추가...")
    vector_store.add_documents(chunks)

    print("5. 검색 테스트...")
    query = "자연어 처리의 정의"
    results = vector_store.db.similarity_search(query, k=2)

    print(f"   쿼리: '{query}'")
    for i, doc in enumerate(results, 1):
        print(f"   결과 {i}: {doc.metadata['title']}")
        print(f"     내용 미리보기: {doc.page_content[:50]}...")

    print("\n✅ 전체 파이프라인 테스트 완료!")


if __name__ == "__main__":
    test_vector_store()
    test_with_kor_chunker()
