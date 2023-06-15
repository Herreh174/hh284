from flask import jsonify
import functions_framework
import os
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotFound, MethodNotAllowed
from database import (
    get_root_system_message,
    set_root_system_message,
    get_chat_messages,
    save_chat_messages,
    clear_chat_messages,
    set_chat_custom_system_message,
    set_chat_system_message)
from gpt import (
    get_chat_completion,
    get_moderation,
    extract_reponse_to_message)

messages_length = os.environ.get('MESSAGES_LENGTH', "20")

def validate_env():
    required_env_vars = [
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_PASSWORD",
        "GPT_API_KEY",
        ]
    for var in required_env_vars:
        if var not in os.environ:
            raise Exception(f"Environment variable {var} not found!")

def clear_chat(request, chat_id):
    clear_chat_messages(chat_id)
    return {}, 200

def set_chat(request, chat_id):
    request_json = request.get_json(silent=True)
    if "content" not in request_json:
        return {"error": "content not in request"}, 400
    message_content = request_json['content']
    messages = get_chat_messages(chat_id, int(messages_length))
    if len(messages) == 0:
        messages.append(set_chat_system_message(chat_id))
    messages.append({"role": "user", "content": message_content})
    response = get_chat_completion(messages)
    response_message, tokens = extract_reponse_to_message(response)
    save_chat_messages(chat_id, 
        [{"role": "user", "content": message_content},
        response_message])
    response_message["tokens"] = tokens
    return jsonify(response_message)

def get_chat(request, chat_id):
    messages = get_chat_messages(chat_id)
    if len(messages) == 0:
        return {"error": f"user {chat_id} has no messages"}, 404
    else:
        return jsonify(messages)

def set_system(request, chat_id):
    if "content" not in request.json:
        return {"error": "content not in request"}, 400
    content = request.json["content"]
    set_chat_custom_system_message(chat_id, content)
    return {}, 200

def get_system(request, chat_id):
    messages = get_chat_messages(chat_id)
    if len(messages) == 0:
        return {"error": f"user {chat_id} has no messages"}, 404
    else:
        return jsonify(messages[0])

def moderation_check(request):
    if "content" not in request.json:
        return {"error": "content not in request"}, 400
    content = request.json["content"]
    response = get_moderation(content)
    return jsonify(response)

def set_root_system(request):
    if "content" not in request.json:
        return {"error": "content not in request"}, 400
    content = request.json["content"]
    set_root_system_message(content)
    return {}, 200

def get_root_system(request):
    message = get_root_system_message()
    return jsonify({"content": message})

# health check
def home(*args):
    return "Hello, World!", 200

url_map = Map([
    Rule('/', methods=['GET', 'POST'], endpoint=home),
    Rule('/system', methods=['GET'], endpoint=get_root_system),
    Rule('/system', methods=['POST'], endpoint=set_root_system),
    Rule('/mod', methods=['POST'], endpoint=moderation_check),
    Rule('/<chat_id>/system', methods=['GET'], endpoint=get_system),
    Rule('/<chat_id>/system', methods=['POST'], endpoint=set_system),
    Rule('/<chat_id>/chat', methods=['GET'], endpoint=get_chat),
    Rule('/<chat_id>/chat', methods=['POST'], endpoint=set_chat),
    Rule('/<chat_id>/clear', methods=['POST'], endpoint=clear_chat),
])

@functions_framework.http
def main(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    validate_env()
    path = request.path
    method = request.method
    print(method, path)
    adapter = url_map.bind_to_environ(request.environ)
    try:
        endpoint, values = adapter.match()
    except (NotFound, MethodNotAllowed):
        return "Not Found", 404
    else:
        return endpoint(request, **values)
