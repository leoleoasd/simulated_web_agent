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

from ..agent.gpt import chat_bedrock as chat
from ..agent.gpt import chat_bulk
from ..executor import amazon_recipes, google_flights_recipes, onestopshop_recipes
from ..executor.env import (
    Browser,  # noqa
    SeleniumEnv,  # noqa
)
from .model import AgentPolicy, HumanPolicy, OpenAIPolicy  # noqa  # noqa


def make_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def solve_captcha(browser: Browser):
    try:
        while True:
            image = browser.driver.find_element(
                By.CSS_SELECTOR,
                "body > div > div.a-row.a-spacing-double-large > div.a-section > div > div > form > div.a-row.a-spacing-large > div > div > div.a-row.a-text-center > img",
            ).get_attribute("src")
            image_file = requests.get(image).content
            image_file = base64.b64encode(image_file).decode("utf-8")
            resp = chat(
                [
                    {
                        "role": "system",
                        "content": 'You are an OCR expert designed to solve CAPTCHAs. You will respond in a single JSON format: {"text": "The text in the image"}. DO NOT include any other text. E.g. {"text": "123456"}',
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_file,
                                },
                            },
                            {"type": "text", "text": "What’s in this image?"},
                        ],
                    },
                ],
                model="anthropic.claude-3-5-sonnet-20240620-v1:0",
                json_mode=True,
            )
            print(resp)
            text = json.loads(resp)["text"]
            input_element = browser.driver.find_element(
                By.CSS_SELECTOR, "#captchacharacters"
            )
            # input_element.send_keys(text)
            # input_element.send_keys(Keys.ENTER)
            for keys in text:
                input_element.send_keys(keys)
                time.sleep(0.2)
            input_element.send_keys(Keys.ENTER)
            time.sleep(1)
    except selenium.common.exceptions.NoSuchElementException:
        # no more captcha
        pass
    return


@click.command()
@click.option("--persona", type=str, help="Path to the persona file.", required=True)
@click.option("--output", type=str, help="Path to the output file.", required=True)
@click.option("--max-steps", type=int, help="Maximum steps to run.", default=50)
@make_sync
async def main(persona: str, output: str, max_steps: int):
    load_dotenv()
    logging.basicConfig()
    loggers = [
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("simulated_web_agent")
    ]
    for logger in loggers:
        logger.setLevel(logging.INFO)
    persona_info = json.load(open(persona))
    persona = persona_info["persona"]
    intent = persona_info["intent"]

    env = gym.make(
        "SeleniumEnv-v0",
        start_url="https://www.amazon.com",
        # start_url="https://www.google.com/flights",
        headless=os.environ.get("HEADLESS", "true").lower() == "true",
        # recipes=google_flights_recipes.recipes,
        recipes=amazon_recipes.recipes,
        start_callback=solve_captcha,
        end_callback=lambda x: print("end with ", x),
    )
    num_steps = 0
    observation, info = env.reset()

    try:
        policy = AgentPolicy(persona, intent, output)

        while True:
            if not observation["error_message"]:
                del observation["error_message"]
            # print(observation["page"])
            clickables = observation["clickables"]
            # print("clickables:", clickables)
            action = await policy.forward(observation, clickables)
            print(f"Taking action {action}")
            observation, reward, terminated, truncated, info = env.step(action)
            print("-" * 50)
            if terminated:
                break
            num_steps += 1
            if num_steps >= max_steps:
                print(f"Reached max steps of {max_steps}, stopping.")
                (policy.run_path / "failed.json").write_text("reached max steps")
                break
    except Exception:
        print(traceback.format_exc())

        (policy.run_path / "error.txt").write_text(traceback.format_exc())
    finally:
        await policy.close()
        env.close()


if __name__ == "__main__":
    main()
