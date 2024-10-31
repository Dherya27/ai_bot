import os
from dsrag.knowledge_base import KnowledgeBase
from dsrag.document_parsing import extract_text_from_pdf
from dotenv import load_dotenv

# # Load environment variables
# env_file_path = ".env"
# load_dotenv(dotenv_path=env_file_path)

# Function to create a kb from a document file -------> (supports both text and PDF)   ## ToDo: add html ##
def create_kb(kb_id: str, file_path: str, storage_directory: str):
    """
    Create a knowledge base (KB) from a given file and save it in the specified storage directory.
    
    Args:
        kb_id (str): Unique identifier for the knowledge base.
        file_path (str): Path to the file from which to create the knowledge base.
        storage_directory (str): Directory where the knowledge base will be stored.
    
    Returns:
        KnowledgeBase: The created knowledge base object.
    """
    doc_id = os.path.basename(file_path).split(".")[0]

    # Determine file type and extract text accordingly
    if file_path.endswith(".pdf"):
        document_text = extract_text_from_pdf(file_path)
    else:
        with open(file_path, "r") as f:
            document_text = f.read()

    # Ensure the text is a string (it might return a tuple by mistake in some cases)
    if isinstance(document_text, tuple):
        document_text = document_text[0]

    # print(f"Document text preview:\n{document_text[:1000]}")

    # Create a new knowledge base or load an existing one
    kb = KnowledgeBase(kb_id=kb_id, exists_ok=True, storage_directory=storage_directory)
    
    # Add the document to the knowledge base
    kb.add_document(doc_id=doc_id, text=document_text)
    # print(f"Document '{doc_id}' added to the knowledge base '{kb_id}'.")
    return kb


# Class for handling the knowledge base operations
class KnowledgeBaseHandler:
    def __init__(self, kb_id: str, storage_directory: str):
        """
        Initialize the KnowledgeBaseHandler to load an existing knowledge base.
        
        Args:
            kb_id (str): Unique identifier for the knowledge base.
            storage_directory (str): Directory where the knowledge base is stored.
        
        Raises:
            ValueError: If the storage directory is not provided.
        """
        if not storage_directory:
            raise ValueError("A valid storage directory must be provided.")
        
        # Load the existing knowledge base from the provided storage directory
        self.kb = KnowledgeBase(kb_id=kb_id, storage_directory=storage_directory, exists_ok=True)
        print(f"Knowledge base '{kb_id}' loaded from {storage_directory}")

    def retrieve_information(self, query: str) -> str:
        """
        Retrieve relevant information from the knowledge base for a given query.
        
        Args:
            query (str): The user's query to search in the knowledge base.
        
        Returns:
            str: The retrieved information or a message if no relevant information is found.
        """
        search_queries = [query]
        results = self.kb.query(search_queries)

        if not results:
            return f"No relevant information found in the knowledge base for the query: {query}"

        retrieved_info = "\n".join([segment["text"] for segment in results])
        return retrieved_info


#Define followings to create kb and add documents
file_path = "documents/kb_arlo.pdf"
kb_id = "arlo"
storage_directory = "database"

# Create the knowledge base and add the document
# kb = create_kb(kb_id, file_path, storage_directory)
# print("Created kb")

# # Load the knowledge base and retrieve information
# kb_handler = KnowledgeBaseHandler(kb_id=kb_id, storage_directory=storage_directory)

# # Check retrieved info based on query
# query = "What is EOL policy?"
# retrieved_info = kb_handler.retrieve_information(query)

# # Display retrieved information
# print(f"Retrieved Information:\n{retrieved_info}")