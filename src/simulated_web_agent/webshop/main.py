import logging

import gymnasium as gym

from ..agent.gpt import chat_bulk
from ..executor.env import SeleniumEnv  # noqa
from .env import WebshopEnv  # noqa
from .model import AgentPolicy, HumanPolicy, OpenAIPolicy  # noqa

if __name__ == "__main__":
    logging.basicConfig()
    personas = {
        "persona": [
            "Background: I am Amir, a 35-year-old urban planner working for a city government, focusing on sustainable development projects to enhance urban living. Demographics: Age: 35, Gender: Male, Education: Master’s degree in Urban Planning. Professional Life: My career is dedicated to revitalizing urban areas with environmental sustainability, collaborating with architects, engineers, and community leaders. Financial Situation: I earn a monthly income of approximately $5,000, prioritizing investments in green technologies and saving for future projects and personal milestones like home ownership. Shopping Habits: I shop infrequently, preferring eco-friendly and ethically produced goods, and support local businesses. Personal Style: My style is minimalist and eco-conscious, consisting of organic fabrics and neutral colors, practical yet polished for office settings and community site visits.",
            "Background: I am Jasmine, a 42-year-old freelance graphic designer specializing in digital marketing and brand development for small businesses and startups. Demographics: Age: 42, Gender: Female, Education: Bachelor's degree in Graphic Design. Professional Life: Working from my home studio, I manage a flexible schedule, juggling multiple projects and nurturing client relationships. Financial Situation: My monthly income varies between $3,000 to $6,000, managing finances by maintaining steady clients and engaging in speculative projects for high returns. Shopping Habits: I enjoy splurging on tech gadgets that enhance my design capabilities, valuing quality over quantity from innovative brands. Personal Style: My style reflects my creative profession with bold prints and vibrant colors, favoring accessories that stand out and comfortable yet stylish attire for my dynamic work-from-home lifestyle.",
            "Background: I am Elliot, a 30-year-old software developer at a tech startup focusing on mobile applications for health and fitness. Demographics: Age: 30, Gender: Male, Education: Bachelor’s degree in Software Engineering. Professional Life: I thrive in the fast-paced environment of my startup, involved in brainstorming, coding, and beta testing. Financial Situation: I earn a monthly income of around $7,000, hopeful about my financial future with salary and company shares, especially if the startup goes public or is acquired. Shopping Habits: I prefer gadgets and software that aid my development work or health monitoring, focusing on the latest tech to support my lifestyle and career. Personal Style: My wardrobe is casual and tech-oriented with smartwatches and fitness trackers, preferring comfortable tech wear suitable for both the office and active lifestyle.",
        ]
    }
    intents = {
        "intent": [
            [
                "I am looking for a men's raincoat. It should be durable and in a neutral color, preferably grey or olive. It should be practical for both commuting and fieldwork, with a budget of up to $150.",
                "I need a pair of men's walking shoes. It should be sturdy, ideal for urban and light outdoor activities. The price should not exceed $120.",
                "I am in search of a men's wallet. It should be minimalist, with a slim design and sufficient space for essentials, priced under $50.",
            ],
            [
                "I am searching for a women's sweater. It should be comfortable for long hours at my desk and stylish enough for client meetings, with a price less than $100.",
                "I need a pair of women's ankle boots. They should be suitable for studio wear and client visits, with a budget up to $150.",
                "I am looking for a women's wallet. It should be unique, graphic-designed that reflects my artistic style, with ample space for cards and essentials, ideally under $60.",
            ],
            [
                "I need a men's tech t-shirt. It should be high-performance, breathable suitable for both coding marathons and my after-work jogging sessions. It should be within a budget of around $50.",
                "I am looking for a pair of running shoes. It should be suitable for daily wear and occasional sports activities. My budget is around $100.",
                "I want a men's wallet. It should be compact, durable with RFID blocking and a sleek design, ideal for tech-savvy users, priced under $40.",
            ],
        ]
    }
    env = gym.make("Webshop-v0")
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
                    print(observation["page"])
                    clickables = observation["clickables"]
                    print("clickables:", clickables)
                    action = policy.forward(observation, clickables)
                    print(f"Taking action {action}")
                    observation, reward, terminated, truncated, info = env.step(action)
                    print("-" * 50)
                    if terminated:
                        break
            finally:
                env.close()
                print(policy.agent.format_memories(policy.agent.memory.memories))
