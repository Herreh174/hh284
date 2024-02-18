# Proxy API for ChatGPT

This proxy API has been designed to add data persistency and chat separation to the ChatGPT API. It provides a layer of abstraction between the users and the ChatGPT API, allowing for easy storage and retrieval of chat sessions.

## Features

- Data persistency: stores chat sessions in a database for easy retrieval.
- Chat separation: separates chats by session, making it easy to retrieve previous chats.
- Easy deployment: designed to run on Google Cloud Functions with a deploy.sh script.

## Requirements

- [Google Cloud](https://cloud.google.com/) account
    - And a project with the [Cloud Functions](https://cloud.google.com/functions) API enabled
- [UpStash](https://upstash.com) account (any Redis provider will work, but this project use UpStash since it has a nice free tier)
- A ChatGPT API key (you can get one [here](https://platform.openai.com))
- Python 3.9 or higher (this is the runtime, you don't need to install Python on your machine unless you want to run the code locally)

## Configuration

Before deploying the proxy API, you'll need to configure the following environment variables:

- `GPT_API_KEY`: your ChatGPT API key
- `REDIS_HOST`: the database number of your UpStash Redis instance
- `REDIS_PORT`: the port of your UpStash Redis instance
- `REDIS_PASSWORD`: the password of your UpStash Redis instance

You can configure these environment variables by copying the `.env.example` file to `.env` and filling in the values. There are also some optional environment variables you can configure, check the `.env.example` file for more information.

## Deploying the Function using the gcloud CLI Tool

> Note: If you have python installed on your machine your can quickly run the function locally using the `functions-framework` package. To do this, run `pip install functions-framework` and then run `export $(cat .env | xargs); functions-framework --target=main` in the root directory of the project. This will start a local server (with all the env vars loaded) on port 8080 which you can use to test the function. **This is not recommended for production use**.

You can deploy this proxy API to Google Cloud Functions using the gcloud CLI tool. Here are the steps to deploy the function:

1. Install the [gcloud CLI tool](https://cloud.google.com/sdk/docs/install) on your machine if not already installed.
2. Navigate to the root directory of the project in your terminal.
3. Use the `gcloud init` command to initialize gcloud and set up your project configuration.
4. Use the `gcloud functions deploy` command to deploy the function to Google Cloud Functions.

```bash
gcloud function deploy <your-function-name> \
    --runtime python39 \
    --region=us-central1 \
    --trigger-http \
    --project <name-of-your-gcp-project> \
    --source . \
    --entry-point main \
    --allow-unauthenticated
```

This will deploy your function with the HTTP trigger. `--allow-unauthenticated` allows unauthenticated access to your function endpoint.

Once the function is deployed, you'll receive a URL which you can use to send requests to and retrieve chat logs for your application.

## Usage

To start using the proxy API, you can make POST requests to the following endpoint:

https://[YOUR_CLOUD_FUNCTION_URL]/<chat_id>/chat

    Where `<chat_id>` is the ID of the chat session you want to retrieve. If the chat session doesn't exist, it will be created automatically, but the chat_id value is up to you.

## API Documentation

#### HealthCheck

<details>
 <summary><code>GET</code> <code><b>/</b></code> <code>(Check service availability)</code></summary>

##### Parameters

> None

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `text/html`                | `Hello, World!`                             |

##### Example cURL

> ```bash
>  curl -X GET http://localhost:8080/
> ```

</details>

#### System prompt

<details>
 <summary><code>GET</code> <code><b>/system</b></code> <code>(Get current global system prompt)</code></summary>

##### Parameters

> None

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | `{"content": "You are a python engineer..."}`                       |

##### Example cURL

> ```bash
>  curl -X GET http://localhost:8080/system
> ```

</details>

<details>
 <summary><code>POST</code> <code><b>/system</b></code> <code>(Set the global system prompt, base for all chats system prompt)</code></summary>

##### Body (JSON)

> | name     | type     | data type  | description                                            |
> |----------|----------|------------|--------------------------------------------------------|
> | content  | required | string     | A message telling how ChatGPT should behave. Check [suggestions](https://github.com/mustvlad/ChatGPT-System-Prompts)


##### Responses

> | http code     | content-type                      | response                       |
> |---------------|-----------------------------------|--------------------------------|
> | `200`         | `application/json`                | `{}`                           |

##### Example cURL

> ```bash
>  curl -X POST -H "Content-Type: application/json" --data @system.json http://localhost:8080/system
> ```

</details>

#### Moderation check

    OpenAI provides moderation checks to users messages, which can help detect unwanted behavior on a conversation.

<details>
 <summary><code>POST</code> <code><b>/mod</b></code> <code>(Send user's messages to this endpoint before calling /chat)</code></summary>

##### Body (JSON)

> | name     | type     | data type  | description                                            |
> |----------|----------|------------|--------------------------------------------------------|
> | content  | required | string     | The message to evaluate possible moderation flags


##### Responses

> | http code     | content-type                      | response                       |
> |---------------|-----------------------------------|--------------------------------|
> | `200`         | `application/json`                | `{"id": "string", "model": "string", "results": [{...}]}`                           |

##### Example cURL

> ```bash
>  curl -X POST -H "Content-Type: application/json" --data @message.json http://localhost:8080/mod
> ```

</details>

#### Chat system prompt

<details>
 <summary><code>POST</code> <code><b>/&lt;chat_id&gt;/system</b></code> <code>(Same as global system prompt but for individual chat)</code></summary>

##### Example cURL

> ```bash
>  curl -X POST -H "Content-Type: application/json" --data @system.json http://localhost:8080/<chat_id>/system
> ```

</details>

<details>
 <summary><code>GET</code> <code><b>/&lt;chat_id&gt;/system</b></code> <code>(Same as global system prompt but for individual chat)</code></summary>

##### Example cURL

> ```bash
>  curl -X GET http://localhost:8080/<chat_id>/system
> ```

</details>

#### Chat conversation

<details>
 <summary><code>POST</code> <code><b>/&lt;chat_id&gt;/chat</b></code> <code>(Send a message to a chat)</code></summary>

##### Body (JSON)

> | name     | type     | data type  | description                                            |
> |----------|----------|------------|--------------------------------------------------------|
> | content  | required | string     | User message to send to ChatGPT and get the response


##### Responses

> | http code     | content-type                      | response                       |
> |---------------|-----------------------------------|--------------------------------|
> | `200`         | `application/json`                | `{"content": "string", "role": "string", "tokens": {"completion_tokens": number, "prompt_tokens": number, "total_tokens": number}}`                           |

##### Example cURL

> ```bash
>  curl -X POST -H "Content-Type: application/json" --data @message.json http://localhost:8080/<chat_id>/chat
> ```

</details>


<details>
 <summary><code>GET</code> <code><b>/&lt;chat_id&gt;/chat</b></code> <code>(Get list of all messages in this chat)</code></summary>

##### Parameters

> None

##### Responses

> | http code     | content-type                      | response                       |
> |---------------|-----------------------------------|--------------------------------|
> | `200`         | `application/json`                | `[{"content": "string", "role": "string"}]`                           |

##### Example cURL

> ```bash
>  curl -X GET http://localhost:8080/<chat_id>/chat
> ```

</details>

#### Send images to a chat


<details>
 <summary><code>POST</code> <code><b>/&lt;chat_id&gt;/img</b></code> <code>(Send a image url to a chat and get the image description)</code></summary>

##### Body (JSON)

> | name     | type     | data type  | description                                            |
> |----------|----------|------------|--------------------------------------------------------|
> | content  | required | string     | A prompt about the image like: "What's on this image?"
> | url      | required | string     | The url of the image


##### Responses

> | http code     | content-type                      | response                       |
> |---------------|-----------------------------------|--------------------------------|
> | `200`         | `application/json`                | `{"content": "string", "role": "string", "tokens": {"completion_tokens": number, "prompt_tokens": number, "total_tokens": number}}`                           |

##### Example cURL

> ```bash
>  curl -X POST -H "Content-Type: application/json" --data @image.json http://localhost:8080/<chat_id>/img
> ```

</details>

#### Clear a chat

<details>
 <summary><code>POST</code> <code><b>/&lt;chat_id&gt;/clear</b></code> <code>(Clear all messages from a chat)</code></summary>

##### Body (JSON)

> None

##### Responses

> | http code     | content-type                      | response                       |
> |---------------|-----------------------------------|--------------------------------|
> | `200`         | `application/json`                | `{}`                           |

##### Example cURL

> ```bash
>  curl -X POST http://localhost:8080/<chat_id>/clear
> ```

</details>

## License

This repository is licensed under the MIT license. See `LICENSE` for more information.