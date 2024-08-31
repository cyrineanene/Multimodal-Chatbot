from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from config_initialization_files.llm_chains import load_vectordb, create_embeddings
#to convert the bytes to adequate format
import pypdfium2

def get_pdf_texts(pdfs_bytes):
    return [extract_text_from_pdf(pdf_bytes) for pdf_bytes in pdfs_bytes]

def extract_text_from_pdf(pdf_bytes):
    pdf_file = pypdfium2.PdfDocument(pdf_bytes)
    return "/n".join(pdf_file.get_page(page_number).get_textpage().get_text_range() for page_number in range(len(pdf_file)))

#Using Document to accommodate for the emnedding model => here tokens are 512
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=50, separators=["\n", "\n\n"])
    return splitter.split_text(text)

def get_document_chunk(text_list):
    documents = []
    for text in text_list:
        for chunk in get_text_chunks(text):
            documents.append(Document(page_content = chunk))
    return documents

def add_documents_to_db(pdfs_bytes):
    texts = get_pdf_texts (pdfs_bytes)
    documents = get_document_chunk(texts)
    vector_db = load_vectordb(create_embeddings())
    vector_db.add_documents(documents)
    print("Documents added to db")