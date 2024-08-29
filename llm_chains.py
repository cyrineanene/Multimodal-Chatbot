from langchain.chains import StuffDocumentsChain, LLMChain, ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from langchain.vectorstores import Chroma
import chromadb
import yaml 
from prompt_templates import memory_prompt_template

#Loading the config file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def create_llm(model_path = config["modal_path"]["large"], model_type=config["model_type"]):
    llm = CTransformers(model_path, model_type)
    return llm

def create_embeddings(embedding_path = config["embeddings_path"]):
    return HuggingFaceInstructEmbeddings(embedding_path)

def create_chat_memory(chat_history):
    return ConversationBufferWindowMemory(memory_key= "history", chat_memory=chat_history, k=3)

def create_prompt_from_template(template):
    return PromptTemplate.from_template(template)

def create_llm_chain(llm, chat_prompt, memory):
    return LLMChain(llm, chat_prompt, memory)

def load_normal_chain(chat_history):
    return chatChain(chat_history)

class chatChain:
    def __init__(self, chat_history, model_path = config["modal_path"]["large"], model_type=config["model_type"]):
        self.memory = create_chat_memory(chat_history)
        llm = create_llm(model_path, model_type)
        chat_prompt = create_prompt_from_template(memory_prompt_template)
        self.llm_chain = create_llm_chain(llm, chat_prompt, self.memory)

    def run(self, user_input):
        return self.llm_chain.run(human_input = user_input, history=self.memory.chat_memory.messages, stop = ["Human: "]) #The stop param is needed so the model won't hallucinate conversations (questions and answers)