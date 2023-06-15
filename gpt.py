import os
import openai

max_tokens = os.environ.get('MAX_TOKENS', "500")
messages_length = os.environ.get('MESSAGES_LENGTH', "20")
openai.api_key = os.environ.get('GPT_API_KEY')

def get_moderation(input):
    response = openai.Moderation.create(input=input)
    return response

def get_chat_completion(
    messages,
    max_tokens=int(max_tokens),
    temperature=0.9,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.6,
):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        max_tokens=max_tokens,
        messages=messages
    )
    return response

def extract_reponse_to_message(response):
    prompt_tokens = response["usage"]["prompt_tokens"]
    completion_tokens = response["usage"]["completion_tokens"]
    total_tokens = response["usage"]["total_tokens"]
    tokens = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }
    content = response["choices"][0]["message"]["content"]
    role = response["choices"][0]["message"]["role"]
    return {"role": role, "content": content}, tokens
