import asyncio
import functools
import json
import logging
import os
import traceback

import click
import gymnasium as gym
from dotenv import load_dotenv

from ..agent.gpt import chat_bulk
from ..executor import google_flights_recipes, onestopshop_recipes
from ..executor.env import SeleniumEnv  # noqa
from .model import AgentPolicy, HumanPolicy, OpenAIPolicy  # noqa


def make_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


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
        start_url="http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:7770/",
        # start_url="https://www.google.com/flights",
        headless=os.environ.get("HEADLESS", "true").lower() == "true",
        # recipes=google_flights_recipes.recipes,
        recipes=onestopshop_recipes.recipes,
    )
    num_steps = 0
    observation, info = env.reset()

    try:
        policy = AgentPolicy(persona, intent, output)

        while True:
            print(observation["url"])
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
