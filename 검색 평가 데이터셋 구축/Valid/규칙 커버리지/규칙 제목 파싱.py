import re
import sys
from pathlib import Path
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


class RuleTitleExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf_loader = PDFLoader(pdf_path)

    def extract_text_from_pdf(self) -> str:
        """PDF에서 모든 텍스트 추출"""
        documents = self.pdf_loader.load()
        full_text = ""
        for doc in documents:
            full_text += doc.page_content + "\n"
        return full_text

    def extract_rule_titles(self, text: str) -> List[str]:
        """< >로 감싸진 규칙 제목 추출"""
        pattern = r"<([^<>]+)>"
        matches = re.findall(pattern, text)

        # 공백 정리 및 중복 제거
        cleaned_titles = []
        for match in matches:
            cleaned = match.strip()
            if cleaned and cleaned not in cleaned_titles:
                cleaned_titles.append(cleaned)

        return cleaned_titles

    def extract_and_display(self) -> List[str]:
        """PDF에서 규칙 제목을 추출하고 결과 출력"""
        print(f"📄 PDF 파일 로딩 중: {self.pdf_path}")

        # PDF 텍스트 추출
        text = self.extract_text_from_pdf()

        # 규칙 제목 추출
        print("🔍 규칙 제목 추출 중...")
        titles = self.extract_rule_titles(text)

        if not titles:
            print("❌ < >로 감싸진 규칙 제목을 찾을 수 없습니다.")
            return []

        # 결과 출력
        print(f"\n✅ {len(titles)}개의 규칙 제목을 찾았습니다:")
        print("-" * 50)
        for i, title in enumerate(titles, 1):
            print(f"{i:3d}. {title}")

        return titles

    def save_to_file(self, titles: List[str], output_file: str = None) -> None:
        """추출된 제목을 파일로 저장"""
        if not output_file:
            pdf_name = Path(self.pdf_path).stem
            output_file = f"{pdf_name}_규칙제목.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("PDF에서 추출된 규칙 제목들\n")
            f.write("=" * 50 + "\n\n")
            for i, title in enumerate(titles, 1):
                f.write(f"{i:3d}. {title}\n")
            f.write(f"\n총 {len(titles)}개의 규칙 제목이 발견되었습니다.\n")

        print(f"✅ 결과가 {output_file}에 저장되었습니다.")


def main():
    """메인 함수"""
    print("📋 PDF 규칙 제목 추출기 (LangChain)")
    print("=" * 40)

    # PDF 파일 경로 입력
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1].strip("\"'")
    else:
        pdf_path = input("PDF 파일 경로를 입력하세요: ").strip().strip("\"'")

    if not pdf_path or not Path(pdf_path).exists():
        print("❌ 파일을 찾을 수 없습니다.")
        return

    try:
        # 규칙 제목 추출기 생성 및 실행
        extractor = RuleTitleExtractor(pdf_path)
        titles = extractor.extract_and_display()

        if titles:
            # 파일 저장 여부 확인
            save_option = (
                input(f"\n결과를 텍스트 파일로 저장하시겠습니까? (y/n): ")
                .strip()
                .lower()
            )
            if save_option in ["y", "yes", "네", "ㅇ"]:
                extractor.save_to_file(titles)

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
