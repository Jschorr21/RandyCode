import csv
from langchain.schema import Document
import os
class CSVLoader:
    """Loads course data from CSV and converts it into LangChain Documents."""

    def __init__(self, file_path):
        self.file_path = os.path.join(os.path.dirname(__file__), file_path)

    def load_documents(self):
        """Reads CSV file and converts rows into LangChain Document objects."""
        documents = []

        with open(self.file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            for row in reader:
                course_code = row[1].split(' -')[0]
                metadata = {'course_code': course_code, 'subject_area': row[0]}
                documents.append(Document(page_content=', '.join(row), metadata=metadata))

        return documents

# Usage:
if __name__ == "__main__":
    csv_loader = CSVLoader("subject_courses.csv")
    course_docs = csv_loader.load_documents()
    print(f"✅ Loaded {len(course_docs)} courses from CSV.")
