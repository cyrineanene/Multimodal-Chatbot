from langchain.chains import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain_community.vectorstores import Chroma
import chromadb
import yaml 
from config_initialization_files.prompt_templates import memory_prompt_template

#Loading the config file
with open("config_initialization_files/config.yaml", "r") as f:
    config = yaml.safe_load(f)

def create_llm(model_path = config["model_path"]["large"], model_type=config["model_type"], model_config = config["model_config"]):
    llm = CTransformers(model=model_path, model_type=model_type, config=model_config)
    return llm

def create_embeddings(embedding_path = config["embeddings_path"]):
    return HuggingFaceInstructEmbeddings(model_name=embedding_path)

def create_chat_memory(chat_history):
    return ConversationBufferWindowMemory(memory_key= "history", chat_memory=chat_history, k=3)

def create_prompt_from_template(template):
    return PromptTemplate.from_template(template)

def create_llm_chain(llm, chat_prompt, memory):
    return LLMChain(llm=llm, prompt=chat_prompt, memory=memory)

def load_normal_chain(chat_history):
    return chatChain(chat_history)

def load_vectordb(embeddings):
    persistent_client = chromadb.PersistentClient('chroma_db') #config["chromadb"]["chromadb_path"]
    langchain_chroma = Chroma(
        client=persistent_client,
        collection_name='pdfs', #config["chromadb"]["collection_name"]
        embedding_function=embeddings,
    )
    return langchain_chroma

def load_pdf_chat_chain(chat_history):
    return pdfChatChain(chat_history)

def load_retrival_chain(llm, memory, vector_db):
    return RetrievalQA.from_llm(llm = llm, memmory=memory, retriever=vector_db.as_retriever())

class pdfChatChain:
    def __init__(self, chat_history):
        self.memory = create_chat_memory(chat_history)
        self.vector_db = load_vectordb(create_embeddings())
        llm=create_llm()
        #chat_prompt = create_prompt_from_template(memory_prompt_template)
        self.llm_chain = load_retrival_chain(llm, self.memory, self.vector_db)
    
    def run(self, user_input):
        return self.llm_chain.run(query=user_input, history=self.memory.chat_memory.messages, stop=["Human:"])

class chatChain:
    def __init__(self, chat_history):
        self.memory = create_chat_memory(chat_history)
        llm = create_llm()
        chat_prompt = create_prompt_from_template(memory_prompt_template)
        self.llm_chain = create_llm_chain(llm, chat_prompt, self.memory)

    def run(self, user_input):
        return self.llm_chain.run(human_input = user_input, history=self.memory.chat_memory.messages, stop = ["Human: "]) #The stop param is needed so the model won't hallucinate conversations (questions and answers)