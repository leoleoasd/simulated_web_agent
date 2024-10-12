import asyncio
import json
import logging
import os
import signal
import subprocess
import time
from pathlib import Path

import click
import gymnasium as gym
import selenium
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from ..agent.gpt import chat_bulk
from ..executor import amazon_recipes, google_flights_recipes, onestopshop_recipes
from ..executor.env import Browser, SeleniumEnv  # noqa
from .batch import make_sync
from .model import AgentPolicy, HumanPolicy, OpenAIPolicy  # noqa

recording_process = None


def start_recording(output_video: str):
    # screencapture -D 1 -v output.mp4
    # start the background process
    global recording_process
    recording_process = subprocess.Popen(
        ["screencapture", "-D", "1", "-v", output_video],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return recording_process


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


def stop_recording(result=None):
    # process.terminate()
    # send Ctrl-C=
    time.sleep(3)
    global recording_process
    recording_process.send_signal(signal.SIGINT)


@click.command()
@click.option("--trace_dir", type=str, help="Directory to replay", required=True)
@click.option("--output-video", type=str, help="Output video file", required=True)
@click.option("--cookie", type=(str, str), help="Cookies to set.")
@make_sync
async def main(trace_dir: str, output_video: str, cookie: list[tuple[str, str]]):
    load_dotenv()
    logging.basicConfig()
    loggers = [
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("simulated_web_agent")
    ]
    for logger in loggers:
        logger.setLevel(logging.INFO)

    env = gym.make(
        "SeleniumEnv-v0",
        start_url="https://www.amazon.com",
        # start_url="https://www.google.com/flights",
        headless=False,
        # recipes=google_flights_recipes.recipes,
        recipes=amazon_recipes.recipes,
        start_callback=lambda x: (
            solve_captcha(x),
            start_recording(output_video),
        ),
        end_callback=lambda x: stop_recording,
    )
    observation, info = env.reset()

    try:
        # policy = HumanPolicy()
        trace_dir: Path = Path(trace_dir)
        action_trace = [
            json.loads(line)
            for line in (trace_dir / "action_trace.txt").open().readlines()
        ]
        for ac in action_trace:
            print(observation["url"])
            print(observation["page"])
            print("clickables:", observation["clickables"])
            print("inputs:", observation["inputs"])
            time.sleep(5)
            observation, reward, terminated, truncated, info = env.step(json.dumps(ac))
    finally:
        stop_recording()
        env.close()


if __name__ == "__main__":
    asyncio.run(main())
