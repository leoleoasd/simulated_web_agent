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
from dotenv import load_dotenv

from ..agent.gpt import chat_bulk
from ..executor import google_flights_recipes, onestopshop_recipes
from ..executor.env import SeleniumEnv  # noqa
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


def stop_recording(result=None):
    # process.terminate()
    # send Ctrl-C=
    time.sleep(3)
    global recording_process
    recording_process.send_signal(signal.SIGINT)


@click.command()
@click.option("--trace_dir", type=str, help="Directory to replay", required=True)
@click.option("--output-video", type=str, help="Output video file", required=True)
@make_sync
async def main(trace_dir: str, output_video: str):
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
        start_url="http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:7770/",
        pretty=True,
        headless=False,
        no_animate=False,
        recipes=onestopshop_recipes.recipes,
        start_callback=lambda: start_recording(output_video),
        end_callback=stop_recording,
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
