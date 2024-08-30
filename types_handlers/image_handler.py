from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
#to convert the bytes to adequate format
import base64

def convert_bytes_to_64(image_bytes):
    encoded_string = base64.b64encode(image_bytes).decode("utf-8")
    return "data:image/jpeg;base64," + encoded_string

def handle_image(image_bytes, user_message):
    chat_handler = Llava15ChatHandler(clip_model_path="models/llava/mmproj-model-f16.gguf")
    llm = Llama(
        model_path="models/llava/ggml-model-q5_k.gguf",
        chat_handler=chat_handler,
        logits_all=True,
        n_ctx=1024
    )
    image_base64 = convert_bytes_to_64(image_bytes)

    outputs = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are an assitant who perfectly describes images."},
            {"role": "user",
             "content": [
                 {"type": "image_url", "image_url": {"url": image_base64}},
                 {"type": "text", "text": user_message}
             ]
            }
        ]
    )

    return outputs["choices"][0]["message"]['content']