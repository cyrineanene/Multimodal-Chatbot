from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
import base64

def convert_nytes_to_64(image_bytes):
    encoded_string = base64.b64encode(image_bytes).decode("utf-8")
    return "data:image/jpeg;base64," + encoded_string

def handle_image(images_bytes, user_message):
    chat_handler = Llava15ChatHandler(clip_model_path="models/llava/mmproj-model-f16.gguf")
    llm = Llama()