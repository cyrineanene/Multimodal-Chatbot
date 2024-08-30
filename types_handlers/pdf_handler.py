from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from llm_chains import load_vectordb, load_embedding
#to convert the bytes to adequate format
import pypdfium2

def get_pdf_texts(pdfs_bytes):
    return [extract_text_from_pdf(pdf_bytes) for pdf_bytes in pdfs_bytes]

def extract_text_from_pdf(pdf_bytes):
    with pypdfium2.PdfDocument(pdf_bytes) as pdf_file:
        return "/n".join(pdf_file.get_page(page_number).get_textpage().get_text_range() for page_number in range(len(pdf_file)))

#Using Document to accommodate for the emnedding model => here tokens are 512
def get_text_chunks(texts):
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=50, seperator=["\n", "\n\n"])
    return [splitter.split_text(text) for text in texts]