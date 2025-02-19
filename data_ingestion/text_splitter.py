import os
import pdfplumber
import json
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextSplitter:
    """Handles text extraction, chunking, and saving for vector storage."""

    def __init__(self, chunk_size=1500, chunk_overlap=250):
        """
        Initializes the text splitter with chunking parameters.
        
        Args:
            chunk_size (int): Max number of characters per chunk.
            chunk_overlap (int): Overlap between chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts text from a PDF file and returns a list of texts per page.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            list: Extracted text per page.
        """
        text_by_page = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""  # Extract text or set empty string if none
                text_by_page.append(text)
        return text_by_page

    def chunk_scraped_text(self, text_list):
        """
        Splits text into overlapping chunks with metadata.

        Args:
            text_list (list): List of page-wise text extracted from a document.

        Returns:
            tuple: (documents, metadatas, ids) for ChromaDB storage.
        """
        documents = []
        metadatas = []
        ids = []

        for doc in text_list:
            # ✅ Extract source metadata
            file_name = doc.metadata["source"]  # Extracted filename
            date_scraped = doc.metadata.get("date_scraped", "Unknown Date")

            # ✅ Ensure the first chunk contains metadata
            text_chunks = self.text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(text_chunks):
                chunk_id = str(uuid.uuid4())  # Unique chunk ID

                # ✅ First chunk includes metadata
                if i == 0:
                    chunk = f"Scraped from: {file_name}\nDate scraped: {date_scraped}\n\n{chunk}"

                documents.append(chunk)
                metadatas.append({"source": file_name, "date_scraped": date_scraped, "chunk_number": i + 1})
                ids.append(chunk_id)

        return documents, metadatas, ids
    
    def chunk_pdf_text(self, text_list):
        """
        Splits text into overlapping chunks with metadata.

        Args:
            text_list (list): List of page-wise text extracted from a document.

        Returns:
            tuple: (documents, metadatas, ids) for ChromaDB storage.
        """
        documents = []
        metadatas = []
        ids = []

        for i, page_text in enumerate(text_list):
            chunks = self.text_splitter.split_text(page_text)
            for chunk in chunks:
                chunk_id = str(uuid.uuid4())  # Generate unique ID
                documents.append(chunk)
                metadatas.append({"source": "catalog", "chunk_number": i + 1})  # Store page number as metadata
                ids.append(chunk_id)

        return documents, metadatas, ids

    def save_chunks_to_json(self, documents, metadatas, ids, output_file):
        """
        Saves extracted chunks to a JSON file inside the data folder.

        Args:
            documents (list): List of chunked text.
            metadatas (list): Metadata (e.g., page numbers).
            ids (list): Unique IDs for each chunk.
            output_file (str): File path to save JSON.
        """
        # Ensure 'data' directory exists
        data_folder = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(data_folder, exist_ok=True)  # Create 'data' folder if it doesn't exist

        # Construct full path for output file
        output_path = os.path.join(data_folder, output_file)
        output_dir = os.path.dirname(output_path)  # Extract directory from full path
        os.makedirs(output_dir, exist_ok=True)  # ✅ Create missing directories

        # Save to JSON
        chunk_data = [
            {"id": ids[i], "text": documents[i], "metadata": metadatas[i]}
            for i in range(len(documents))
        ]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, indent=4)

        print(f"✅ Extracted {len(documents)} chunks. Saved to {output_path}.")

# Usage Example
if __name__ == "__main__":
    pdf_path = os.path.join(os.path.dirname(__file__), "data", "Undergraduate_Catalog_2024-25.pdf")  # Ensure the PDF path is correct
    splitter = TextSplitter()
    
    # Extract text
    text_list = splitter.extract_text_from_pdf(pdf_path)
    
    # Chunk text
    documents, metadatas, ids = splitter.chunk_text(text_list)

    # Save chunks to JSON inside 'data/' folder
    splitter.save_chunks_to_json(documents, metadatas, ids)
