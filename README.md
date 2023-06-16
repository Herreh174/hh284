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

    Where `<chat_id>` is the ID of the chat session you want to retrieve. If the chat session doesn't exist, it will be created automatically.

The body of the request should be a JSON object with the following structure:
    
```json
{
    "content": "Hello, how are you?"
}
```
Where `content` is the message you want to send to the chatbot.

A GET request to the same endpoint will return the chat history for the specified chat session.

## License

This repository is licensed under the MIT license. See `LICENSE` for more information.