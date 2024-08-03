import json
import logging

import gymnasium as gym

from ..agent.gpt import chat_bulk
from ..executor.env import SeleniumEnv  # noqa
from .model import AgentPolicy, HumanPolicy, OpenAIPolicy  # noqa

if __name__ == "__main__":
    logging.basicConfig()
    env = gym.make(
        "SeleniumEnv-v0",
        start_url="http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:7770/",
        pretty=True,
        headless=True,
    )
    observation, info = env.reset()

    try:
        policy = HumanPolicy()
        for ac in [
            {
                "type": "type",
                "name": "header.search_box.search_input",
                "text": "woman jacket",
            },
            {"type": "click", "name": "header.search_box.search_button"},
            {
                "type": "click",
                "name": "search_results.woman_within_womens_plus_size_zipfront_microfleece_jacket_fleece.view_product",
            },
        ]:
            print(observation["url"])
            print(observation["page"])
            print("clickables:", observation["clickables"])
            print("inputs:", observation["inputs"])
            observation, reward, terminated, truncated, info = env.step(json.dumps(ac))

        while True:
            print(observation["url"])
            print(observation["page"])
            print("clickables:", observation["clickables"])
            print("inputs:", observation["inputs"])
            action = policy.forward(observation, observation["clickables"])
            print(f"Taking action {action}")
            observation, reward, terminated, truncated, info = env.step(action)
            print("-" * 50)
            if terminated:
                break
    finally:
        env.close()
