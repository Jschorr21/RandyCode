import sys
import os

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_ingestion.vector_store import VectorStore
from data_ingestion.text_splitter import TextSplitter
from data_ingestion.csv_loader import CSVLoader

class CoursesPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        self.text_splitter = TextSplitter()

    def run(self):
        # Step 3: Load course data from CSV
        csv_path = os.path.join(os.path.dirname(__file__), "data", "subject_courses.csv")
        csv_loader = CSVLoader(csv_path)
        course_documents = csv_loader.load_documents()

        if not self.vector_store.stores["courses"]:
            self.vector_store.add_new_store("courses")

        # Step 4: Store in vector database
        self.vector_store.add_documents(course_documents, store_type="courses")

# Run pipeline
if __name__ == "__main__":
    ingestion = CoursesPipeline()
    ingestion.run()