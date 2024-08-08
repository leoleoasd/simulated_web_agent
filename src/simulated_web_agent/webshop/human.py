import json
import logging
import os
import time

import gymnasium as gym
from dotenv import load_dotenv

from ..agent.gpt import chat_bulk
from ..executor.env import SeleniumEnv  # noqa
from .model import AgentPolicy, HumanPolicy, OpenAIPolicy  # noqa

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig()
    env = gym.make(
        "SeleniumEnv-v0",
        start_url="http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:7770/",
        pretty=True,
        headless=os.environ.get("HEADLESS", "true").lower() == "true",
    )
    observation, info = env.reset()

    try:
        policy = HumanPolicy()
        for ac in [
            {"type": "type_and_submit", "name": "header.search_box.search_input", "text": "waterproof coat", "description": "Type 'waterproof coat' in the search input box and submit the query."}
            # {
            #     "type": "click",
            #     "name": "product_showcases.v8_energy_healthy_energy_drink_steady_energy_from_black_and_green_tea_pomegranate_blueberry_8_ounce_can_pack_of_24.view_product",
            # },
            # {
            #     "type": "click",
            #     "name": "product_info.reviews_12",
            # },
            # {
            #     "type": "type",
            #     "name": "header.search_box.search_input",
            #     "text": "woman jacket",
            # },
            # {"type": "click", "name": "header.search_box.search_button"},
            # {
            #     "type": "click",
            #     "name": "search_results.woman_within_womens_plus_size_zipfront_microfleece_jacket_fleece.view_product",
            # },
            # {
            #     "type": "back",
            # },
            # {"type": "click", "name": "search_results.women_outwear_jacket_autumn_and_winter_longsleeved_lapel_buttoned_solid_color_plush_warm_jacket_gifts_for_ladies.view_product"},
            # {
            #     "type": "back",
            # },
            # {
            #     "type": "click",
            #     "name": "search_results.woman_within_womens_plus_size_packable_puffer_jacket.view_product"
            # },
            # {"type": "click", "name": "options.black"},
            # {"type": "click", "name": "options.medium_plus"},
            # {"type": "click", "name": "add_to_cart"},
        ]:
            print(observation["url"])
            print(observation["page"])
            print("clickables:", observation["clickables"])
            print("inputs:", observation["inputs"])
            observation, reward, terminated, truncated, info = env.step(json.dumps(ac))
            time.sleep(1)

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
