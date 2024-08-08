import logging
import os
import traceback

import gymnasium as gym
from dotenv import load_dotenv

from ..agent.gpt import chat_bulk
from ..executor.env import SeleniumEnv  # noqa
from .model import AgentPolicy, HumanPolicy, OpenAIPolicy  # noqa

if __name__ == "__main__":
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
Professional Life:
Clara spends most of her time in academia, attending conferences, working in the lab, and writing papers. Her commitment to her research is her main priority, and she manages her time around her academic responsibilities.

Financial Situation:
Clara lives on her stipend as a PhD student and is careful with her spending. She prefers to save money for research-related expenses and invest in her academic pursuits.


Shopping Habits:
Clara dislikes shopping and avoids spending much time browsing through products. She prefers straightforward, efficient shopping experiences and often shops online for convenience. When she does shop, she looks for practicality and affordability over style or trendiness.
So Clara want to shop QUICKLY and EFFICIENTLY.

Personal Style:
Clara prefers comfortable, functional clothing, often choosing items that are easy to wear for long hours spent at her desk or in the lab. She wears small-sized clothing and likes colors that reflect her personality—mostly red, which she finds uplifting and energizing."""
        ]
    }
    intents = {
        "intent": [
            [
                "I'm looking for a jacket.",
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
        start_url="http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:7770/",
        headless=os.environ.get("HEADLESS", "true").lower() == "true",
    )
    for index, persona in enumerate(personas["persona"]):
        print(f"Persona {index}: {persona}")
        for intent in intents["intent"][index]:
            print(f"Intent: {intent}")
            observation, info = env.reset()

            try:
                policy = AgentPolicy(persona, intent)
                policy.agent.add_thought("I should shorter search terms.")

                while True:
                    print(observation["url"])
                    # print(observation["page"])
                    clickables = observation["clickables"]
                    # print("clickables:", clickables)
                    action = policy.forward(observation, clickables)
                    print(f"Taking action {action}")
                    observation, reward, terminated, truncated, info = env.step(action)
                    print("-" * 50)
                    if terminated:
                        break
            except Exception as e:
                print(traceback.format_exc())

                (policy.run_path / "error.txt").write_text(traceback.format_exc())
            finally:
                env.close()
