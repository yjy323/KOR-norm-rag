import argparse
import datetime
import json
import logging
import math
import os
from typing import Any, Callable, Dict, List

from tqdm import tqdm

from src.knowledge_base.embedding.sentence_transformers_embedding import (
    SentenceTransformersEmbedding,
)
from src.knowledge_base.retrieval.vector_store_retriever import VectorStoreRetriever

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_dataset(file_path: str) -> List[Dict[str, Any]]:
    """JSON 데이터셋을 로드합니다."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"데이터셋 파일을 찾을 수 없습니다: {file_path}")
        raise
    except json.JSONDecodeError:
        logging.error(f"데이터셋 파일이 올바른 JSON 형식이 아닙니다: {file_path}")
        raise


def save_results(results: Dict[str, Any], output_dir: str):
    """평가 결과를 파일에 저장합니다."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_dir, f"retriever_evaluation_log_{timestamp}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    logging.info(f"평가 결과를 {file_path}에 저장했습니다.")


def _create_query_from_answer(item: Dict[str, Any]) -> str:
    """
    output.answer를 기반으로 평가 쿼리를 생성합니다.
    '옳다.'를 기준으로 분리하거나, 없을 경우 전체 answer를 사용합니다.
    """
    answer = item.get("output", {}).get("answer", "")
    if not answer:
        # answer가 비어있으면 input.question을 fallback으로 사용
        return item.get("input", {}).get("question", "")

    separator = "옳다."
    query = answer.strip()  # 기본적으로 전체 답변을 쿼리로 사용

    separator_pos = answer.find(separator)
    if separator_pos != -1:
        # '옳다.'가 발견되면 그 뒤의 텍스트를 쿼리로 사용 시도
        query_candidate = answer[separator_pos + len(separator) :].strip()
        if query_candidate:
            # '옳다.' 뒤에 내용이 있으면 쿼리로 채택
            query = query_candidate
    return query


def evaluate_retriever_metrics(
    test_data: List[Dict[str, Any]],
    retrieve_function: Callable[[str], List[str]],
    k_values: List[int],
) -> tuple[Dict[int, Dict[str, float]], List[Dict[str, Any]]]:
    """
    RAG 검색 시스템의 검색 성능 지표를 계산합니다.

    Args:
        test_data (list): 평가 데이터셋. 각 항목은 {"input": {"question": str}, "output": {"article": str}} 형태.
                          `output.article`은 해당 질문에 대한 단일 정답 문서의 ID를 나타냅s니다.
        retrieve_function (callable): 사용자 쿼리(str)를 받아 검색된 문서 ID 리스트(list[str])를 반환하는 함수.
                                      검색된 문서 리스트는 관련성이 높은 순서로 정렬되어 있어야 합니다.
        k_values (list): 평가할 상위 K 값들의 리스트.

    Returns:
        tuple: (평균 지표 dict, 검색 로그 리스트)
    """
    metrics_sums = {
        k: {
            "recall": 0.0,
            "precision": 0.0,
            "f1": 0.0,
            "mrr": 0.0,
            "map": 0.0,
            "ndcg": 0.0,
        }
        for k in k_values
    }
    num_queries = len(test_data)
    search_logs = []

    if num_queries == 0:
        return {
            k: {metric: 0.0 for metric in metrics_sums[k]} for k in k_values
        }, search_logs

    for item in tqdm(test_data, desc="Evaluating Retriever"):
        query = _create_query_from_answer(item)
        relevant_doc_id = item["output"]["article"]

        retrieved_docs = retrieve_function(query)

        search_log = {
            "query": query,
            "relevant_doc_id": relevant_doc_id,
            "retrieved_docs": retrieved_docs,
            "hit_found": relevant_doc_id in retrieved_docs,
        }
        search_logs.append(search_log)

        first_hit_rank = -1
        try:
            first_hit_rank = retrieved_docs.index(relevant_doc_id)
        except ValueError:
            first_hit_rank = -1

        for k in k_values:
            is_hit_at_k = first_hit_rank != -1 and first_hit_rank < k

            recall_at_k_val = 1.0 if is_hit_at_k else 0.0
            metrics_sums[k]["recall"] += recall_at_k_val

            precision_at_k_val = (1.0 / k) if is_hit_at_k else 0.0
            metrics_sums[k]["precision"] += precision_at_k_val

            if (precision_at_k_val + recall_at_k_val) > 0:
                f1_score_at_k_val = (
                    2
                    * (precision_at_k_val * recall_at_k_val)
                    / (precision_at_k_val + recall_at_k_val)
                )
                metrics_sums[k]["f1"] += f1_score_at_k_val

            if is_hit_at_k:
                reciprocal_rank = 1.0 / (first_hit_rank + 1)
                metrics_sums[k]["mrr"] += reciprocal_rank
                metrics_sums[k][
                    "map"
                ] += reciprocal_rank  # For single relevant doc, MAP is same as MRR
                metrics_sums[k]["ndcg"] += 1.0 / math.log2(first_hit_rank + 2)

    final_metrics = {}
    for k in k_values:
        final_metrics[k] = {
            "recall": metrics_sums[k]["recall"] / num_queries,
            "precision": metrics_sums[k]["precision"] / num_queries,
            "f1": metrics_sums[k]["f1"] / num_queries,
            "mrr": metrics_sums[k]["mrr"] / num_queries,
            "map": metrics_sums[k]["map"] / num_queries,
            "ndcg": metrics_sums[k]["ndcg"] / num_queries,
        }

    return final_metrics, search_logs


def main(args):
    """메인 실행 함수"""
    logging.info("평가를 시작합니다.")

    # 1. 데이터셋 로드
    logging.info(f"데이터셋 로딩: {args.dataset_path}")
    eval_dataset = load_dataset(args.dataset_path)

    # 2. 임베딩 모델 및 Retriever 초기화
    logging.info(f"임베딩 모델 및 Retriever 초기화 중: {args.model_name}")
    embedding_model = SentenceTransformersEmbedding(model_name=args.model_name)
    retriever = VectorStoreRetriever(
        vector_store_path=args.vector_store_path,
        embedding_model=embedding_model,
    )
    logging.info("초기화 완료.")

    # 3. 검색 함수 정의
    k_values = [int(k) for k in args.k_values.split(",")]
    max_k = max(k_values)

    def retrieve_function(query: str) -> List[str]:
        retrieved_docs = retriever.search(query=query, k=max_k)
        return [doc.metadata.get("title", "") for doc in retrieved_docs]

    # 4. 평가 수행
    logging.info(f"k={k_values}에 대한 평가를 수행합니다.")

    eval_metrics, search_logs = evaluate_retriever_metrics(
        eval_dataset, retrieve_function, k_values
    )

    results = {
        "model_name": args.model_name,
        "dataset": args.dataset_path,
        "vector_store": args.vector_store_path,
        "evaluation_time": datetime.datetime.now().isoformat(),
        "k_values": k_values,
        "metrics": eval_metrics,
        "logs": search_logs,
    }

    # 5. 결과 출력 및 저장
    print("\n--- 검색 시스템 성능 평가 결과 ---")
    for k, metrics in results["metrics"].items():
        print(f"\n--- Metrics for k={k} ---")
        for metric_name, value in metrics.items():
            print(f"{metric_name.capitalize()}: {value:.4f}")
    print("------------------------------------")
    save_results(results, args.output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG Retriever 성능 평가 스크립트")
    parser.add_argument(
        "--dataset_path",
        type=str,
        default="data/korean_language_retriever_V1.0_train.json",
        help="평가 데이터셋 파일 경로",
    )
    parser.add_argument(
        "--vector_store_path",
        type=str,
        default="data/knowledge_base/korean_rag_reference",
        help="FAISS 벡터 저장소 경로",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        help="사용할 Sentence Transformer 모델 이름",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="logs",
        help="평가 결과 로그를 저장할 디렉토리",
    )
    parser.add_argument(
        "--k_values",
        type=str,
        default="1,3,5,10",
        help="평가를 수행할 k 값들의 쉼표로 구분된 리스트",
    )
    args = parser.parse_args()
    main(args)
