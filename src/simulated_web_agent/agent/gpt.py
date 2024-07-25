import asyncio
from pathlib import Path

import openai

client = openai.Client()
async_client = openai.AsyncClient()
embedding_model = "text-embedding-3-small"
chat_model = "gpt-4o-mini"
prompt_dir = Path(__file__).parent.absolute() / "prompts"


def embed_text(texts, model=embedding_model, **kwargs):
    return client.embeddings.create(input=texts, model=model, **kwargs)


def chat(messages, model=chat_model, **kwargs):
    return client.chat.completions.create(model=model, messages=messages, **kwargs)


def chat_bulk(messages, model=chat_model, **kwargs):
    if len(messages) == 1:
        return [chat(messages[0], model=model, **kwargs)]

    async def chat_one(message):
        return await async_client.chat.completions.create(
            model=model, messages=message, **kwargs
        )

    async def run_all():
        return await asyncio.gather(*[chat_one(m) for m in messages])

    results = asyncio.run(run_all())
    return results


def load_prompt(prompt_name):
    return (prompt_dir / f"{prompt_name}.txt").read_text()
