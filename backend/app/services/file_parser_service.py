import fitz
from docx import Document


class FileParserService:

    def parse_pdf(self, file_path: str):
        text = ""
        pdf = fitz.open(file_path)

        for page in pdf:
            text += page.get_text()

        return text

    def parse_docx(self, file_path: str):
        doc = Document(file_path)
        text = []

        for para in doc.paragraphs:
            text.append(para.text)

        return "\n".join(text)

    def parse_txt(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def parse_file(self, file_path: str, filename: str):
        filename = filename.lower()

        if filename.endswith(".pdf"):
            return self.parse_pdf(file_path)

        elif filename.endswith(".docx"):
            return self.parse_docx(file_path)

        elif filename.endswith(".txt"):
            return self.parse_txt(file_path)

        else:
            raise Exception("Unsupported file type")