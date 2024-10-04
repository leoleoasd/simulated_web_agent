import asyncio
import base64
import json
import logging
import os
import time
import traceback

import gymnasium as gym
import requests
import selenium
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from ..agent.gpt import chat_bedrock as chat
from ..executor import amazon_recipes, google_flights_recipes, onestopshop_recipes
from ..executor.env import Browser, SeleniumEnv  # noqa
from .model import AgentPolicy, HumanPolicy, OpenAIPolicy  # noqa


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
                        "content": 'You are an OCR expert designed to solve CAPTCHAs. You will respond in a single JSON format: {"text": "The text in the image"}',
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
                response_format={"type": "json_object"},
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


async def main():
    load_dotenv()
    logging.basicConfig()
    loggers = [
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("simulated_web_agent")
    ]
    for logger in loggers:
        logger.setLevel(logging.INFO)
    personas = {
        "persona": [
            # "Background: I am Amir, a 35-year-old urban planner working for a city government, focusing on sustainable development projects to enhance urban living. Demographics: Age: 35, Gender: Male, Education: Master’s degree in Urban Planning. Professional Life: My career is dedicated to revitalizing urban areas with environmental sustainability, collaborating with architects, engineers, and community leaders. Financial Situation: I earn a monthly income of approximately $5,000, prioritizing investments in green technologies and saving for future projects and personal milestones like home ownership. Shopping Habits: I shop infrequently, preferring eco-friendly and ethically produced goods, and support local businesses. Personal Style: My style is minimalist and eco-conscious, consisting of organic fabrics and neutral colors, practical yet polished for office settings and community site visits.",
            # "Background: I am Jasmine, a 42-year-old freelance graphic designer specializing in digital marketing and brand development for small businesses and startups. Demographics: Age: 42, Gender: Female, Education: Bachelor's degree in Graphic Design. Professional Life: Working from my home studio, I manage a flexible schedule, juggling multiple projects and nurturing client relationships. Financial Situation: My monthly income varies between $3,000 to $6,000, managing finances by maintaining steady clients and engaging in speculative projects for high returns. Shopping Habits: I enjoy splurging on tech gadgets that enhance my design capabilities, valuing quality over quantity from innovative brands. Personal Style: My style reflects my creative profession with bold prints and vibrant colors, favoring accessories that stand out and comfortable yet stylish attire for my dynamic work-from-home lifestyle.",
            # "Background: I am Elliot, a 30-year-old software developer at a tech startup focusing on mobile applications for health and fitness. Demographics: Age: 30, Gender: Male, Education: Bachelor’s degree in Software Engineering. Professional Life: I thrive in the fast-paced environment of my startup, involved in brainstorming, coding, and beta testing. Financial Situation: I earn a monthly income of around $7,000, hopeful about my financial future with salary and company shares, especially if the startup goes public or is acquired. Shopping Habits: I prefer gadgets and software that aid my development work or health monitoring, focusing on the latest tech to support my lifestyle and career. Personal Style: My wardrobe is casual and tech-oriented with smartwatches and fitness trackers, preferring comfortable tech wear suitable for both the office and active lifestyle.",
            """Persona: Clara
Background:
Clara is a PhD student in Computer Science at a prestigious university. She is deeply engaged in research focusing on artificial intelligence and machine learning, aiming to contribute to advancements in technology that can benefit society.

Demographics:

Age: 28
Gender: Female
Education: Pursuing a PhD in Computer Science
Clara loves United Airlines, and usually wake up at 9am everyday.
Clara lives in Boston.

Financial Situation:
Clara lives on her stipend as a PhD student and is careful with her spending. She prefers to save money for research-related expenses and invest in her academic pursuits.

Shopping Habits:
Clara dislikes shopping and avoids spending much time browsing through products. She prefers straightforward, efficient shopping experiences and often shops online for convenience. When she does shop, she looks for practicality and affordability over style or trendiness.
So Clara want to shop QUICKLY and EFFICIENTLY.

Professional Life:
Clara spends most of her time in academia, attending conferences, working in the lab, and writing papers. Her commitment to her research is her main priority, and she manages her time around her academic responsibilities.

Personal Style:
Clara prefers comfortable, functional clothing, often choosing items that are easy to wear for long hours spent at her desk or in the lab. She wears medium-sized clothing and likes colors that reflect her personality—mostly red, which she finds uplifting and energizing."""
        ]
    }
    intents = {
        "intent": [
            [
                "buy a jacket from columbia and arrives tomorrow.",
                # "book a flight to new york on 10/10/2024, and return on 10/15/2024",
            ]
            # [
            #     "I am looking for a men's raincoat. It should be durable and in a neutral color, preferably grey or olive. It should be practical for both commuting and fieldwork, with a budget of up to $150.",
            #     "I need a pair of men's walking shoes. It should be sturdy, ideal for urban and light outdoor activities. The price should not exceed $120.",
            #     "I am in search of a men's wallet. It should be minimalist, with a slim design and sufficient space for essentials, priced under $50.",
            # ],
            # [
            #     "I am searching for a women's sweater. It should be comfortable for long hours at my desk and stylish enough for client meetings, with a price less than $100.",
            #     "I need a pair of women's ankle boots. They should be suitable for studio wear and client visits, with a budget up to $150.",
            #     "I am looking for a women's wallet. It should be unique, graphic-designed that reflects my artistic style, with ample space for cards and essentials, ideally under $60.",
            # ],
            # [
            #     "I need a men's tech t-shirt. It should be high-performance, breathable suitable for both coding marathons and my after-work jogging sessions. It should be within a budget of around $50.",
            #     "I am looking for a pair of running shoes. It should be suitable for daily wear and occasional sports activities. My budget is around $100.",
            #     "I want a men's wallet. It should be compact, durable with RFID blocking and a sleek design, ideal for tech-savvy users, priced under $40.",
            # ],
        ]
    }
    env = gym.make(
        "SeleniumEnv-v0",
        start_url="https://www.amazon.com",
        # start_url="https://www.google.com/flights",
        headless=os.environ.get("HEADLESS", "true").lower() == "true",
        # recipes=google_flights_recipes.recipes,
        recipes=amazon_recipes.recipes,
        start_callback=solve_captcha,
    )
    for index, persona in enumerate(personas["persona"]):
        print(f"Persona {index}: {persona}")
        for intent in intents["intent"][index]:
            print(f"Intent: {intent}")
            observation, info = env.reset()

            try:
                policy = AgentPolicy(persona, intent)

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
            except Exception:
                print(traceback.format_exc())

                (policy.run_path / "error.txt").write_text(traceback.format_exc())
            finally:
                await policy.close()
                env.close()


if __name__ == "__main__":
    asyncio.run(main())
