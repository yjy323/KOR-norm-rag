# Korean Grammar RAG MVP

> 한국어 어문 규범 기반 생성(RAG) 모델 - 최소 기능 제품(MVP)

## 📚 지식베이스 사용법

### 1. 파이프라인 최초 실행 (지식베이스 구축)

```bash
python -m src.knowledge_base.pipeline
```

구축된 파일 위치: `data/knowledge_base/korean_rag_reference/`

### 2. Retriever 사용법 (모델 개발용)

```python
from src.knowledge_base.retrieval.vector_store_retriever import VectorStoreRetriever
from src.knowledge_base.embedding.sentence_transformers_embedding import SentenceTransformersEmbedding

# 임베딩 모델 초기화
embedding_model = SentenceTransformersEmbedding()

# 검색기 초기화
retriever = VectorStoreRetriever(
    vector_store_path="data/knowledge_base/korean_rag_reference",
    embedding_model=embedding_model
)

# 질문으로 관련 문서 검색
results = retriever.search("맞춤법 규칙을 알려주세요", k=3)

# 컨텍스트 문자열로 변환
context = "\n\n".join([doc.page_content for doc in results])
```

## 🚀 점진적 개선 로드맵

### Week 1: MVP 완성 ✅
- [x] 지식베이스 구축 완료
- [ ] 베이스라인 모델 개발
