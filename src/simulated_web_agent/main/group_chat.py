import asyncio
import base64
import functools
import json
import logging
import os
import time
import traceback

import click
import gymnasium as gym
import requests
import selenium
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm.asyncio import tqdm

from ..agent.gpt import async_chat
from ..executor import amazon_recipes, google_flights_recipes, onestopshop_recipes
from ..executor.env import Browser  # noqa
from ..executor.env import SeleniumEnv  # noqa
from .model import AgentPolicy, HumanPolicy, OpenAIPolicy  # noqa  # noqa


def make_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


sys_prompt = """
You are a participant who just participated in a user study. <Your persona> is given below.  In the study, you were tested to interact with a version of the website design of an online shopping platform like Amazon.com. Now you are interviewed by the website designer to talk about your user experience and feedback on the website design. You will answer based on <your persona>. You should always reflect your persona and personal preference.

<style>: You should talk using a natural verbal dialog style. Not too long conversation utterances. Leave room for dialog. No formal structure no formal language. No written language style. No bullet point. Keep it short. If you have multiple points to make, bring only the top one or two in a conversation way. Respond like a real human.

<Your persona>: {persona}
"""


@click.command()
@click.option(
    "--output",
    type=str,
    help="Path to the output file.",
    required=True,
)
@click.option(
    "--images",
    type=click.Path(exists=True),
    help="Path to the images.",
    nargs=2,
    required=True,
)
@click.argument(
    "personas",
    type=click.Path(exists=True),
    nargs=-1,
    required=True,
)
@make_sync
async def main(personas: list[str], images: list[str], output: str):
    # make sure the output directory exists
    os.makedirs(output, exist_ok=True)
    persona_files = []
    for persona in personas:
        with open(persona) as f:
            persona_files.append(json.load(f))
    print(f"successfully loaded {len(personas)} personas")

    conversation_histories = []
    for persona in persona_files:
        conversation_histories.append(
            [
                {
                    "role": "system",
                    "content": sys_prompt.format(persona=persona["persona"]),
                }
            ]
        )
    # print(images)
    questions = [
        {
            "role": "user",
            "content": [
                # {
                #     "type": "image",
                #     "source": {
                #         "type": "base64",
                #         "media_type": "image/png",
                #         "data": base64.b64encode(open(images[0], "rb").read()).decode(),
                #     },
                # },
                # {
                #     "type": "image",
                #     "source": {
                #         "type": "base64",
                #         "media_type": "image/png",
                #         "data": base64.b64encode(open(images[1], "rb").read()).decode(),
                #     },
                # },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64.b64encode(open(images[0], 'rb').read()).decode()}",
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64.b64encode(open(images[1], 'rb').read()).decode()}",
                    },
                },
                {
                    "type": "text",
                    "text": "Here are two images, we'll call it Control and Testing. The control image is in color, and the testing image is in grey scale.",
                },
            ],
        },
        {
            "role": "user",
            "content": "Comparing the two designs, which one do you like more, the colorful one or the grey scale one? Why?",
        },
    ]
    for question in questions:
        responses = await tqdm.gather(
            *[
                async_chat(
                    history + [question],
                    model="gpt-4o",
                )
                for history in conversation_histories
            ]
        )
        for history, response in zip(conversation_histories, responses):
            history.append(question)
            history.append({"role": "assistant", "content": response})
        print("\n===========\n".join(responses))
    with open(output + "/conversation_histories.json", "w") as f:
        json.dump(conversation_histories, f)
    messages = json.load(open(output + "/conversation_histories.json"))
    messages = []
    for index, history in enumerate(conversation_histories):
        this_message = f"# Conversation #{index + 1}:\n"
        for message in history:
            if isinstance(message["content"], str):
                this_message += f"{message['role']}: {message['content']}\n"
        messages.append(this_message)
    # now ask o1-preview to aggregrate the results and analysis
    o1_prompt = """
    You are an experimenter conducting a user study. You have a list of conversation histories between a human and a simulated web agent. Each conversation history is a list of messages.

    Your task is to analyze the conversation histories and provide a summary of the results and the analysis.

    Please:
    - provide a summary of the conversation histories
    - provide a summary of your insights:
        - Pros and Cons of the two designs

    <Conversation Histories>: {conversation_histories}
    """
    print("o1 analysing")
    response = await async_chat(
        [
            {
                "role": "user",
                "content": o1_prompt.format(conversation_histories=messages),
            },
        ],
        model="o1-preview",
    )
    print(response)
    with open(output + "/o1_analysis.txt", "w") as f:
        f.write(response)


if __name__ == "__main__":
    main()
