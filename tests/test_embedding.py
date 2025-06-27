#!/usr/bin/env python3
"""
SentenceTransformersEmbedding 기능 테스트 스크립트

이 스크립트는 SentenceTransformersEmbedding 클래스의 모든 주요 기능을 테스트합니다.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import numpy as np

from knowledge_base.embedding.sentence_transformers_embedding import (
    SentenceTransformersEmbedding,
)


def test_basic_functionality():
    """기본 기능 테스트"""
    print("=" * 50)
    print("기본 기능 테스트 시작")
    print("=" * 50)

    # 임베딩 객체 생성
    embedding = SentenceTransformersEmbedding()

    # 모델 정보 확인
    info = embedding.get_model_info()
    print(f"모델 정보: {info}")

    # 임베딩 차원 확인
    dim = embedding.get_embedding_dim()
    print(f"임베딩 차원: {dim}")

    print("✅ 기본 초기화 테스트 통과")


def test_single_text_embedding():
    """단일 텍스트 임베딩 테스트"""
    print("\n" + "=" * 50)
    print("단일 텍스트 임베딩 테스트 시작")
    print("=" * 50)

    embedding = SentenceTransformersEmbedding()

    # 단일 텍스트 임베딩
    text = "안녕하세요. 이것은 테스트 문장입니다."
    result = embedding.embed_text(text)

    print(f"입력 텍스트: {text}")
    print(f"임베딩 벡터 shape: {result.shape}")
    print(f"임베딩 벡터 일부: {result[:5]}")

    # 유효성 검증
    assert isinstance(result, np.ndarray), "결과가 numpy array가 아닙니다"
    assert len(result.shape) == 1, "임베딩 벡터가 1차원이 아닙니다"
    assert (
        result.shape[0] == embedding.get_embedding_dim()
    ), "임베딩 차원이 일치하지 않습니다"

    print("✅ 단일 텍스트 임베딩 테스트 통과")


def test_batch_text_embedding():
    """배치 텍스트 임베딩 테스트"""
    print("\n" + "=" * 50)
    print("배치 텍스트 임베딩 테스트 시작")
    print("=" * 50)

    embedding = SentenceTransformersEmbedding()

    # 여러 텍스트 임베딩
    texts = [
        "첫 번째 테스트 문장입니다.",
        "두 번째 테스트 문장입니다.",
        "세 번째 테스트 문장입니다.",
    ]

    result = embedding.embed_texts(texts)

    print(f"입력 텍스트 개수: {len(texts)}")
    print(f"임베딩 벡터 배열 shape: {result.shape}")

    # 유효성 검증
    assert isinstance(result, np.ndarray), "결과가 numpy array가 아닙니다"
    assert len(result.shape) == 2, "임베딩 배열이 2차원이 아닙니다"
    assert result.shape[0] == len(
        texts
    ), "텍스트 개수와 임베딩 개수가 일치하지 않습니다"
    assert (
        result.shape[1] == embedding.get_embedding_dim()
    ), "임베딩 차원이 일치하지 않습니다"

    print("✅ 배치 텍스트 임베딩 테스트 통과")


def test_chunk_embedding():
    """청크 임베딩 테스트"""
    print("\n" + "=" * 50)
    print("청크 임베딩 테스트 시작")
    print("=" * 50)

    embedding = SentenceTransformersEmbedding()

    # 청크 데이터
    chunks = [
        {"content": "첫 번째 청크의 내용입니다.", "metadata": {"page": 1}},
        {"content": "두 번째 청크의 내용입니다.", "metadata": {"page": 2}},
        {"content": "세 번째 청크의 내용입니다.", "metadata": {"page": 3}},
    ]

    result = embedding.embed_chunks(chunks)

    print(f"청크 개수: {len(chunks)}")
    print(f"임베딩 벡터 배열 shape: {result.shape}")

    # 유효성 검증
    assert isinstance(result, np.ndarray), "결과가 numpy array가 아닙니다"
    assert result.shape[0] == len(chunks), "청크 개수와 임베딩 개수가 일치하지 않습니다"
    assert (
        result.shape[1] == embedding.get_embedding_dim()
    ), "임베딩 차원이 일치하지 않습니다"

    print("✅ 청크 임베딩 테스트 통과")


def test_query_embedding():
    """쿼리 임베딩 테스트"""
    print("\n" + "=" * 50)
    print("쿼리 임베딩 테스트 시작")
    print("=" * 50)

    embedding = SentenceTransformersEmbedding()

    # 검색 쿼리
    query = "테스트 문서를 찾고 있습니다"
    result = embedding.embed_query(query)

    print(f"검색 쿼리: {query}")
    print(f"임베딩 벡터 shape: {result.shape}")

    # 유효성 검증
    assert isinstance(result, np.ndarray), "결과가 numpy array가 아닙니다"
    assert len(result.shape) == 1, "임베딩 벡터가 1차원이 아닙니다"
    assert (
        result.shape[0] == embedding.get_embedding_dim()
    ), "임베딩 차원이 일치하지 않습니다"

    print("✅ 쿼리 임베딩 테스트 통과")


def test_similarity_computation():
    """유사도 계산 테스트"""
    print("\n" + "=" * 50)
    print("유사도 계산 테스트 시작")
    print("=" * 50)

    embedding = SentenceTransformersEmbedding()

    # 유사한 텍스트들
    text1 = "강아지가 공원에서 뛰어놀고 있습니다."
    text2 = "개가 공원에서 놀고 있어요."
    text3 = "고양이가 집에서 잠을 자고 있습니다."

    # 임베딩 생성
    emb1 = embedding.embed_text(text1)
    emb2 = embedding.embed_text(text2)
    emb3 = embedding.embed_text(text3)

    # 코사인 유사도 계산
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    sim_1_2 = cosine_similarity(emb1, emb2)
    sim_1_3 = cosine_similarity(emb1, emb3)
    sim_2_3 = cosine_similarity(emb2, emb3)

    print(f"텍스트1: {text1}")
    print(f"텍스트2: {text2}")
    print(f"텍스트3: {text3}")
    print(f"\n유사도 결과:")
    print(f"텍스트1 vs 텍스트2: {sim_1_2:.4f}")
    print(f"텍스트1 vs 텍스트3: {sim_1_3:.4f}")
    print(f"텍스트2 vs 텍스트3: {sim_2_3:.4f}")

    # 유사한 텍스트(1,2)가 다른 텍스트(3)보다 더 유사해야 함
    assert sim_1_2 > sim_1_3, "유사한 텍스트의 유사도가 더 높지 않습니다"
    assert sim_1_2 > sim_2_3, "유사한 텍스트의 유사도가 더 높지 않습니다"

    print("✅ 유사도 계산 테스트 통과")


def test_error_handling():
    """에러 처리 테스트"""
    print("\n" + "=" * 50)
    print("에러 처리 테스트 시작")
    print("=" * 50)

    embedding = SentenceTransformersEmbedding()

    # 빈 텍스트 테스트
    try:
        embedding.embed_text("")
        assert False, "빈 텍스트에 대한 에러가 발생하지 않았습니다"
    except ValueError:
        print("✅ 빈 텍스트 에러 처리 테스트 통과")

    # 빈 리스트 테스트
    try:
        embedding.embed_texts([])
        assert False, "빈 리스트에 대한 에러가 발생하지 않았습니다"
    except ValueError:
        print("✅ 빈 리스트 에러 처리 테스트 통과")

    # 잘못된 청크 형식 테스트
    try:
        embedding.embed_chunks([{"wrong_key": "content"}])
        assert False, "잘못된 청크 형식에 대한 에러가 발생하지 않았습니다"
    except ValueError:
        print("✅ 잘못된 청크 형식 에러 처리 테스트 통과")


def main():
    """메인 테스트 함수"""
    print("SentenceTransformersEmbedding 기능 테스트 시작\n")

    try:
        test_basic_functionality()
        test_single_text_embedding()
        test_batch_text_embedding()
        test_chunk_embedding()
        test_query_embedding()
        test_similarity_computation()
        test_error_handling()

        print("\n" + "=" * 50)
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
