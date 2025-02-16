from PyPDF2 import PdfReader

class PDFParser:
    """Parses Vanderbilt PDF documents (e.g., undergraduate catalog)."""

    def parse_catalog(self, file_path="data/catalog.pdf"):
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() for page in reader.pages])
