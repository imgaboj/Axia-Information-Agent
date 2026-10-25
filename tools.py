from dotenv import load_dotenv
import json
import requests
import os

load_dotenv(override=True)
"""
pushh = {"pushover_user":"PUSHOVER-USER", "pushover_token":"PUSHOVER_TOKEN", "pushover_url":"PUSHOVER_URL"}

for var, push_env in pushh.items():
"""

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token=os.getenv("PUSHOVER_TOKEN")
pushover_url= "https://api.pushover.net/1/messages.json"

def push (text):
    requests.post(
        pushover_url,
        data={
            "user": pushover_user,
            "token": pushover_token,
            "message":text,
        },
    )

#Funcion para registrar datos e emails

def record_user_details (email, name="Name not porvided", notes="Not provided"):
    push(f"Registrando a {name} con el email {email} y notas{notes}")
    return "OK"

def record_unknown_question (question):
    push(f"Registrando {question} esta pregunta que me hicieron y que no pude responder")
    return "OK"

#Creamos sus respectivos json para cada uno de los tools

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {
                "type": "string",
                "description": "Any additional info about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

#Ahora creamos la reacción a nuestra herramienta (Aun no ejecuta ninguna función, solo anticipa que hacer)

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
    ]

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question
    }

#OJO: Necesito repasar esta función y lo que hace:

def handle_tool (tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Herramienta llamada {tool_name}", flush=True)
        tool = tool_map.get(tool_name)
        result = tool(**arguments) 
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    return results