import re
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class KORChunker:
    def __init__(self, documents: List[Document], document_name: str = None):
        self._documents = documents
        self._document_name = document_name or "unknown"

    def _split_blocks_by_title(self, text: str, pattern: str) -> List[str]:
        """정규표현식으로 텍스트를 분할하되 구분자를 유지"""
        matches = list(re.finditer(pattern, text))
        if not matches:
            return [text] if text.strip() else []

        blocks = []
        start = 0

        for match in matches:
            # 이전 블록이 있으면 추가
            if match.start() > start:
                prev_block = text[start : match.start()].strip()
                if prev_block:
                    blocks.append(prev_block)
            start = match.start()

        # 마지막 블록 추가
        if start < len(text):
            last_block = text[start:].strip()
            if last_block:
                blocks.append(last_block)

        return blocks

    def _extract_title_and_content(
        self, block: str, page: int, chunk_id: int
    ) -> Document:
        match = re.match(r"<([^>]+)>\n?(.*)", block, re.DOTALL)
        if match:
            title, body = match.groups()
        else:
            title, body = "unknown", block
        return Document(
            page_content=body.strip(),
            metadata={
                "title": title.strip(),
                "page": page,
                "chunk_id": f"KOR-Regulation-{chunk_id:05d}",
                "source": self._document_name,
            },
        )

    def _split_long_chunks(self, doc: Document) -> List[Document]:
        if len(doc.page_content) < 1000:
            return [doc]
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        sub_texts = splitter.split_text(doc.page_content)
        return [
            Document(page_content=txt, metadata=doc.metadata.copy())
            for txt in sub_texts
        ]

    def process(self) -> List[Document]:
        full_text = "\n".join([doc.page_content for doc in self._documents])
        raw_blocks = self._split_blocks_by_title(full_text, r"(?=<[^>]+>)")
        documents = [
            self._extract_title_and_content(block, page=i // 3 + 1, chunk_id=idx)
            for idx, (i, block) in enumerate(enumerate(raw_blocks))
            if block.strip()
        ]
        final_chunks = []
        for doc in documents:
            final_chunks.extend(self._split_long_chunks(doc))
        return final_chunks
