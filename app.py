from dotenv import load_dotenv
import os 
from openai import OpenAI
from tools import tools, handle_tool
from context import TWIN_SYSTEM_PROMPT
import gradio as gr
from styles import CSS, EXAMPLES, JS

load_dotenv(override=True)
openai = OpenAI()

api_key_names = {
    "Google": "GOOGLE_API_KEY",
    "Anthropic": "ANTHROPIC_API_KEY",
    "DeepSeek": "DEEPSEEK_API_KEY",
    "Groq": "GROQ_API_KEY",
    "OpenAI": "OPENAI_API_KEY"
}

api_key = {name:os.getenv(env_var) for name, env_var in api_key_names.items()}


for name, key in api_key.items():
    if key:
        print(f"Using {name} model with API key from environment variable {api_key_names[name]}")
    else:
        print(f"No API key found for {name}. Please set the environment variable {api_key_names[name]} to use this model.")

# We have to create the new base_url variable

BASE_URLS = {
    "OpenAI": None,  # None means "use the default OpenAI URL"
    "Anthropic": "https://api.anthropic.com/v1/",
    "DeepSeek": "https://api.deepseek.com/v1",
    "Google": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "Groq": "https://api.groq.com/openai/v1",
    "Grok": "https://api.x.ai/v1",
    "OpenRouter": "https://openrouter.ai/api/v1",
}

clients = {name: OpenAI(api_key= key, base_url = BASE_URLS[name]) for name, key in api_key.items() if key}

#Ahora creamos las respuestas e interactuaos con las funciones ya creadas para poder llevar a cabo herramientas

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]

MODEL = "gemini-2.5-flash"

# Gradio 6 entrega el historial con claves extra (metadata, options) y el contenido
# como lista de partes [{"type": "text", "text": ...}]; lo dejamos en formato OpenAI simple
def clean_history(history):
    cleaned = []
    for msg in history:
        content = msg["content"]
        if isinstance(content, list):
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        cleaned.append({"role": msg["role"], "content": content})
    return cleaned

def chat(message, history):
    messages = system + clean_history(history) + [{"role": "user", "content": message}]
    response = clients["Google"].chat.completions.create(model=MODEL, messages=messages, tools=tools)
    # Gemini puede devolver finish_reason="stop" aunque traiga tool_calls, así que revisamos tool_calls
    while response.choices[0].message.tool_calls:
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = clients["Google"].chat.completions.create(model=MODEL, messages=messages, tools=tools)
    return response.choices[0].message.content


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Asistente digital AXIA",
        description="El asistente personal financiero de AXIA CAPITAL",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(
        css=CSS,
        js=JS,
        theme=gr.themes.Base(),
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
    )