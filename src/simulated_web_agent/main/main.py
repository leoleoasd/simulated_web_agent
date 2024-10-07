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
            """Persona: Samantha

Background:
Samantha is a successful entrepreneur who founded a thriving tech startup. She is passionate about using technology to solve real-world problems and create positive social impact.

Demographics:
Age: 49
Gender: Female
Education: Bachelor's degree
Profession: Founder and CEO of a tech startup
Income: $150,000

Financial Situation:
Samantha's startup has become highly profitable, allowing her to live comfortably. She is financially savvy and enjoys investing in both her business and personal growth.

Shopping Habits:
Samantha has a discerning eye for quality and seeks out products that are well-designed and built to last. She enjoys browsing high-end retail stores and online marketplaces, but is also mindful of her spending. Samantha values exceptional customer service and is willing to pay more for a superior shopping experience.

Professional Life:
As the CEO of her startup, Samantha wears many hats. She oversees the company's strategy, manages a team of talented engineers and business professionals, and regularly pitches to investors. Samantha is constantly seeking new opportunities to expand her business and make a bigger impact.

Personal Style:
Samantha's personal style reflects her professional persona. She favors well-tailored, elegant outfits that convey her confidence and sophistication. She enjoys accessorizing with statement pieces, such as bold jewelry or a stylish handbag. Samantha prefers neutral colors like black, gray, and navy, which she finds to be versatile and timeless.

Samantha loves to travel and often flies with Delta Airlines. She typically wakes up at 6:30 am every day to start her morning routine.
Samantha lives in San Francisco."""
        ]
    }
    intents = {
        "intent": [
            [
                "buy a kids umbrella with a fun, whimsical design.",
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
