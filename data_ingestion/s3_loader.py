import boto3
from langchain_core.documents import Document

class S3Loader:
    """Handles loading raw text files from S3."""

    def __init__(self, bucket_name, prefix, region="us-east-1"):
        """
        Initializes the S3Loader.

        Args:
            bucket_name (str): S3 bucket name.
            prefix (str): Folder path inside the bucket.
            region (str): AWS region.
        """
        self.s3_client = boto3.client("s3", region_name=region)
        self.bucket_name = bucket_name
        self.prefix = prefix

    def load_documents(self):
        """
        Fetches all `.txt` files from S3 and returns them as raw LangChain Document objects.

        Returns:
            List[Document]: List of documents with file contents and metadata.
        """
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.prefix)

        documents = []

        for obj in response.get("Contents", []):
            file_key = obj["Key"]
            
            if not file_key.endswith(".txt"):  
                continue  # ✅ Only process .txt files
            
            file_response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            content = file_response["Body"].read().decode("utf-8")
            
            documents.append(Document(page_content=content, metadata={"source": file_key}))

        return documents
