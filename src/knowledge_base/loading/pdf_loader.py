from typing import List

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader


class PDFLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Document]:
        """PDF를 페이지 단위로 로딩"""
        loader = PyPDFLoader(self.file_path)
        return loader.load()
