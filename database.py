import json
import os
import redis

redis_host = os.environ.get('REDIS_HOST')
redis_port = os.environ.get('REDIS_PORT')
redis_pass = os.environ.get('REDIS_PASSWORD')
expire_hours = os.environ.get('EXPIRE_HOURS', "6")
default_expiration = 60 * 60 * int(expire_hours)

redis_client = redis.Redis(host=redis_host,
                port=redis_port,
                password=redis_pass,
                decode_responses=True)

def clear_chat_messages(chat_id):
    redis_client.delete(f"user-{chat_id}")

def save_chat_messages(chat_id, messages):
    if not messages:
        return
    for message in messages:
        redis_client.rpush(f"user-{chat_id}", json.dumps(message))
    redis_client.expire(f"user-{chat_id}", default_expiration)

def set_chat_custom_system_message(chat_id, message=None):
    content = message or get_root_system_message()
    new_system_message = {"role": "system", "content": content}
    if not redis_client.exists(f"user-{chat_id}"):
        redis_client.rpush(f"user-{chat_id}", json.dumps(new_system_message))
        redis_client.expire(f"user-{chat_id}", default_expiration)
        return
    redis_client.lset(f"user-{chat_id}", 0, json.dumps(new_system_message))
    redis_client.expire(f"user-{chat_id}", default_expiration)

def set_chat_system_message(chat_id):
    system_message = get_root_system_message()
    message = {
        "role": "system",
        "content": system_message
    }
    redis_client.rpush(f"user-{chat_id}", json.dumps(message))
    redis_client.expire(f"user-{chat_id}", default_expiration)
    return message

def get_chat_messages(chat_id, number_of_messages=-1):
    first_item = redis_client.lindex(f"user-{chat_id}", 0)
    if not first_item:
        return []
    first_item = json.loads(first_item)
    if first_item.get("role") != "system":
        redis_client.delete(f"user-{chat_id}")
        return []
    last_n_items = redis_client.lrange(f"user-{chat_id}", -number_of_messages, -1)
    last_n_items = [json.loads(item) for item in last_n_items]
    if first_item not in last_n_items:
        last_n_items.insert(0, first_item)
    return last_n_items

def get_root_system_message():
    message = redis_client.get("system")
    return message

def set_root_system_message(message):
    if not message:
        return
    redis_client.set("system", message)
