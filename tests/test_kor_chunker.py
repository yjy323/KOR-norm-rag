import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.knowledge_base.chunking.kor_chunker import KORChunker
from src.knowledge_base.loading.pdf_loader import PDFLoader


def test_rag_chunking():
    pdf_path = "data/국어 지식 기반 생성(RAG) 참조 문서.pdf"
    preview = 3

    # Step 1: Load PDF
    loader = PDFLoader(pdf_path)
    docs = loader.load()
    print(f"[INFO] PDF에서 {len(docs)}개의 페이지를 로드했습니다.")

    # Step 2: Chunk 처리
    chunker = KORChunker(docs, document_name=pdf_path.split("/")[-1])
    chunks = chunker.process()
    print(f"[INFO] 총 {len(chunks)}개의 청크가 생성되었습니다.")

    # Step 3: 일부 청크 출력
    for i, chunk in enumerate(chunks[:preview]):
        print(f"\n--- 청크 {i+1} ---")
        print(f"제목: {chunk.metadata.get('title')}")
        print(f"페이지: {chunk.metadata.get('page')}")
        print(f"ID: {chunk.metadata.get('chunk_id')}")
        print(f"내용:\n{chunk.page_content[:300]} (...)")


if __name__ == "__main__":
    test_rag_chunking()
