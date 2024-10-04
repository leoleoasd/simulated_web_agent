import asyncio
import json
import time
from pathlib import Path
from typing import Any

import aioboto3
import boto3
import openai
from openai.types import CreateEmbeddingResponse
from openai.types.chat import ChatCompletion

from . import context

# client = openai.Client()
# async_client = openai.AsyncClient()
# client = None
client = None
async_client = None
# embedding_model = "text-embedding-3-small"
embedding_model = "cohere.embed-english-v3"
# chat_model = "gpt-4o-mini"
chat_model = "anthropic.claude-3-haiku-20240307-v1:0"
prompt_dir = Path(__file__).parent.absolute() / "shop_prompts"
import botocore

session = aioboto3.Session()


def async_retry(times=10):
    def func_wrapper(f):
        async def wrapper(*args, **kwargs):
            wait = 1
            max_wait = 5
            for _ in range(times):
                # noinspection PyBroadException
                try:
                    return await f(*args, **kwargs)
                except Exception as exc:
                    print("got exc", exc)
                    await asyncio.sleep(wait)
                    wait = min(wait * 2, max_wait)
                    pass
            raise exc

        return wrapper

    return func_wrapper


def retry(times=10):
    def func_wrapper(f):
        def wrapper(*args, **kwargs):
            wait = 1
            max_wait = 5
            for _ in range(times):
                # noinspection PyBroadException
                try:
                    return f(*args, **kwargs)
                except Exception as exc:
                    print("got exc", exc)
                    # await asyncio.sleep(wait)
                    time.sleep(wait)
                    wait = min(wait * 2, max_wait)
                    pass
            raise exc

        return wrapper

    return func_wrapper


@async_retry()
async def embed_text_bedrock(
    texts: list[str], model=embedding_model, type="search_document", **kwargs
) -> list[list[float]]:
    async with session.client("bedrock-runtime", region_name="us-east-1") as client:
        response = await client.invoke_model(
            modelId=model,
            body=json.dumps(
                {
                    "texts": texts,
                    "input_type": type,
                    "truncate": "END",
                }
            ),
        )
        result = json.loads(await response["body"].read())
        return result["embeddings"]


@async_retry()
async def async_chat_bedrock(
    messages: list[dict[str, str]],
    model=chat_model,
    log=True,
    json_mode=False,
    **kwargs,
) -> ChatCompletion:
    async with session.client("bedrock-runtime", region_name="us-east-1") as client:
        if context.api_call_manager and log:
            context.api_call_manager.request.append(messages)
        system_message = messages[0]["content"]
        messages = messages[1:]
        response = await client.invoke_model(
            modelId=model,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 5000,
                    "system": system_message,
                    "messages": messages,
                }
            ),
        )
        result = json.loads(await response["body"].read())
        content = result["content"][0]["text"]
        if context.api_call_manager and log:
            context.api_call_manager.response.append(content)

        if json_mode:
            # Extract JSON substring from the content
            try:
                json_str = _extract_json_string(content)
                json_obj = json.loads(json_str)
                return json_str
            except Exception as e:
                print(e)
                print(content)
                print(json_str)
                raise Exception("Invalid JSON in response") from e
        else:
            return content


def _extract_json_string(text: str) -> str:
    import regex

    # Improved pattern to match JSON objects. Note: This is still not foolproof for deeply nested or complex JSON.
    json_pattern = r"\{(?:[^{}]*|(?R))*\}"
    matches = regex.findall(json_pattern, text, regex.DOTALL)
    if matches:
        return matches[0]
    else:
        raise Exception("No JSON object found in the response")


@retry()
def chat_bedrock(messages: list[dict[str, str]], model=chat_model, **kwargs) -> str:
    client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    system_message = messages[0]["content"]
    messages = messages[1:]
    response = client.invoke_model(
        modelId=model,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 5000,
                "system": system_message,
                "messages": messages,
            }
        ),
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


async def embed_text(texts, model=embedding_model, **kwargs) -> CreateEmbeddingResponse:
    try:
        embeds = await async_client.embeddings.create(
            input=texts, model=model, **kwargs
        )
        return [e.embedding for e in embeds.data]
    except Exception as e:
        print(texts)
        print(e)
        raise e


def chat(messages, model=chat_model, **kwargs) -> ChatCompletion:
    try:
        return client.chat.completions.create(model=model, messages=messages, **kwargs)
    except Exception as e:
        print(messages)
        print(e)
        raise e


async def async_chat(messages, model=chat_model, log=True, **kwargs) -> ChatCompletion:
    try:
        if context.api_call_manager and log:
            context.api_call_manager.request.append(messages)
        response = await async_client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )
        if context.api_call_manager and log:
            context.api_call_manager.response.append(
                response.choices[0].message.content
            )
        return response
    except Exception as e:
        print(messages)
        print(e)
        raise e


def chat_bulk(messages, model=chat_model, **kwargs):
    if len(messages) == 1:
        return [chat(messages[0], model=model, **kwargs)]

    async def run_all():
        return await asyncio.gather(
            *[async_chat(m, model=model, **kwargs) for m in messages]
        )

    results = asyncio.run(run_all())
    return results


def load_prompt(prompt_name):
    return (prompt_dir / f"{prompt_name}.txt").read_text()
