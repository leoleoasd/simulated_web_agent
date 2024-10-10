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
    "--input_file",
    type=click.Path(exists=True),
    help="Path to the conversation history.",
    required=True,
)
@make_sync
async def main(input_file: str, output: str):
    conversation_history = json.load(open(input_file))
    while True:
        question = input("Enter a question: ")
        if question == "":
            break
        response = await async_chat(
            conversation_history + [{"role": "user", "content": question}],
            model="gpt-4o",
        )
        conversation_history.append({"role": "user", "content": question})
        conversation_history.append({"role": "assistant", "content": response})
        print(response)

    with open(output, "w") as f:
        json.dump(conversation_history, f)


if __name__ == "__main__":
    main()
