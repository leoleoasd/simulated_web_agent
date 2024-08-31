from ..agent.gpt import chat
import asyncio, json
from pathlib import Path
from tqdm.asyncio import tqdm


async def main():
    output_dir = Path("personas")
    income_level = [
        (0, 30000),
        (30001, 58020),
        (58021, 94000),
        (94001, 153000),
        (153001, 1000000),
    ]
    gender = ["male", "female", "non-binary"]
    base_intent = "buy a jacket"
    i = 0
    t = tqdm(total=len(income_level) * len(gender) * 4)
    for income in income_level:
        for g in gender:
            for _ in range(4):
                persona = chat(
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a helpful assistant that generates persona. 
    Example:
    Persona: Clara
    Background:
    Clara is a PhD student in Computer Science at a prestigious university. She is deeply engaged in research focusing on artificial intelligence and machine learning, aiming to contribute to advancements in technology that can benefit society.

    Demographics:

    Age: 28
    Gender: Female
    Education: Pursuing a PhD in Computer Science
    Profession: PhD student
    Income: $50,000

    Financial Situation:
    Clara lives on her stipend as a PhD student and is careful with her spending. She prefers to save money for research-related expenses and invest in her academic pursuits.

    Shopping Habits:
    Clara dislikes shopping and avoids spending much time browsing through products. She prefers straightforward, efficient shopping experiences and often shops online for convenience. When she does shop, she looks for practicality and affordability over style or trendiness.
    So Clara want to shop QUICKLY and EFFICIENTLY.

    Professional Life:
    Clara spends most of her time in academia, attending conferences, working in the lab, and writing papers. Her commitment to her research is her main priority, and she manages her time around her academic responsibilities.

    Personal Style:
    Clara prefers comfortable, functional clothing, often choosing items that are easy to wear for long hours spent at her desk or in the lab. She wears medium-sized clothing and likes colors that reflect her personality—mostly red, which she finds uplifting and energizing.
    Clara loves United Airlines, and usually wake up at 9am everyday.
    Clara lives in Boston.
    """,
                        },
                        {
                            "role": "user",
                            "content": f"Generate a persona for a {g} who is a {income[0]} income level.",
                        },
                    ]
                )
                print(persona.choices[0].message.content)
                persona = persona.choices[0].message.content
                intent = chat(
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a helpful assistant that generates intent for a persona. The persona is {persona}.",
                        },
                        {
                            "role": "user",
                            "content": f"""Generate a specificied intent for the persona. The intent is {base_intent}. Examples of specific intent:
Input:
buy a jacket
Output:
buy a red, medium-sized woman's jacket.
Only output the specified intent, no other text.
    """,
                        },
                    ]
                )
                print(intent.choices[0].message.content)
                intent = intent.choices[0].message.content
                json.dump(
                    {
                        "persona": persona,
                        "intent": intent,
                        "income": income,
                        "gender": g,
                    },
                    (output_dir / f"{i}.json").open("w"),
                )
                i += 1
                t.update(1)


if __name__ == "__main__":
    asyncio.run(main())
