# It suits the format required by mistral models: check https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF for more infos
memory_prompt_template = """<s>[INST] You are an AI chatbot having a conversation with a human. Answer his questions.[/INST]
    Previous conversation: {history}
    Human: {human_input}
    AI: """