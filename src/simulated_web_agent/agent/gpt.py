import asyncio
from pathlib import Path
from typing import Any

import openai
from openai.types import CreateEmbeddingResponse
from openai.types.chat import ChatCompletion

from . import context

client = openai.Client()
async_client = openai.AsyncClient()
embedding_model = "text-embedding-3-small"
chat_model = "gpt-4o-mini"
prompt_dir = Path(__file__).parent.absolute() / "shop_prompts"


async def embed_text(texts, model=embedding_model, **kwargs) -> CreateEmbeddingResponse:
    try:
        return await async_client.embeddings.create(input=texts, model=model, **kwargs)
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
