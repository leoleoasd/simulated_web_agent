import asyncio
import json
import random
import re
from pathlib import Path

import click
import yaml
from tqdm.contrib.concurrent import thread_map  # or thread_map

from ..agent.gpt import chat_bedrock as chat
from .batch import make_sync


def parse_range(range_str):
    """Parse a range string like '18-24' and return a tuple (18, 24)."""
    match = re.match(r"(\d+)[\s]*-[\s]*(\d+)", range_str)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        raise ValueError(f"Invalid range format: '{range_str}'")


def prepare_cumulative_distribution(ratio_dict):
    """Prepare cumulative distribution for sampling."""
    items = list(ratio_dict.items())
    total_ratio = sum(ratio_dict.values())
    cumulative = []
    cumulative_prob = 0
    for k, v in items:
        cumulative_prob += v / total_ratio
        cumulative.append((cumulative_prob, k))
    return cumulative


def sample_from_cumulative(cumulative):
    """Sample a key based on the cumulative distribution."""
    r = random.random()
    for prob, k in cumulative:
        if r <= prob:
            return k
    return cumulative[-1][1]  # In case of rounding errors


@click.command()
@click.option(
    "--config-file",
    type=str,
    required=True,
    help="Path to the YAML configuration file containing parameters.",
)
@make_sync
async def main(config_file: str):
    # Load configuration from YAML file
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    output_dir = Path(config["output_dir"])
    json_output_dir = output_dir / "json"
    human_readable_output_dir = output_dir / "prettified"

    json_output_dir.mkdir(parents=True, exist_ok=True)
    human_readable_output_dir.mkdir(parents=True, exist_ok=True)

    total_personas = config.get("total_personas", 20)

    # Read queries from file
    queries_file = config["queries_file"]
    with open(queries_file, "r") as f:
        base_queries = [line.strip() for line in f if line.strip()]

    if not base_queries:
        print("The queries file is empty. Please provide at least one query.")
        return

    # Load demographic distributions from config
    age_groups = config["age_groups"]
    genders = config["genders"]
    income_groups = config["income_groups"]

    # pretty print the config
    for key in ["age_groups", "genders", "income_groups"]:
        print(f"distribution for {key}:")
        for k, v in config[key].items():
            print(f"  {k}: {v:.1f}%")
        print("-----------------")

    # Prepare cumulative distributions for sampling
    age_cumulative = prepare_cumulative_distribution(age_groups)
    gender_cumulative = prepare_cumulative_distribution(genders)
    income_cumulative = prepare_cumulative_distribution(income_groups)

    previous_personas = []  # List to store previous personas

    def generate_one(i):
        # Sample age group, then parse age range from group key
        age_group = sample_from_cumulative(age_cumulative)
        age_range = parse_range(age_group)
        age = random.randint(*age_range)

        # Sample gender
        gender = sample_from_cumulative(gender_cumulative)

        # Sample income group, parse income range
        income_group = sample_from_cumulative(income_cumulative)
        income_range = parse_range(income_group)

        # Prepare examples
        if previous_personas:
            # Randomly select one or more previous personas as examples
            num_examples = min(len(previous_personas), 3)
            examples = random.sample(previous_personas, num_examples)
            example_text = "\n\n".join(examples)
        else:
            # Use initial seed persona as example
            example_text = config["example_persona"]

        # Generate persona
        persona_response = chat(
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a helpful assistant that generates diverse personas.
Examples:
{example_text}
""",
                },
                {
                    "role": "user",
                    "content": f"""Generate a persona using the above examples. The persona should be different from previous personas to ensure diversity. The persona should:

- Have the age of {age}
- Be {gender}
- Have an income between ${income_range[0]} and ${income_range[1]}

Provide the persona in the same format as the examples.

Only output the persona, no other text.
""",
                },
            ]
        )

        persona = persona_response.strip()

        previous_personas.append(persona)  # Add current persona to list

        # Select a random base query from the queries file
        base_query = random.choice(base_queries)

        # Generate intent
        intent_response = chat(
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a helpful assistant that generates specific intents for a persona. The persona is:

{persona}

""",
                },
                {
                    "role": "user",
                    "content": f"""Generate a specified intent for the persona, based on a search query. The search query is "{base_query}". The intent should always be to buy something. Examples of specific intents:

Input:
jacket columbia

Output:
buy a red, medium-sized woman's jacket from Columbia.

Only output the specific intent, no other text.
The output intent should be executable on a shopping website.
""",
                },
            ]
        )

        intent = intent_response.strip()

        # Save JSON
        with (json_output_dir / f"virtual customer {i}.json").open("w") as f_json:
            json.dump(
                {
                    "persona": persona,
                    "intent": intent,
                    "age": age,
                    "age_group": age_group,
                    "gender": gender,
                    "income": income_range,
                    "income_group": income_group,
                },
                f_json,
                indent=4,
            )

        # Save human-readable format
        with (human_readable_output_dir / f"virtual customer {i}.txt").open(
            "w"
        ) as f_txt:
            f_txt.write(persona + "\n")
            f_txt.write("\nIntent:\n")
            f_txt.write(intent + "\n")

    thread_map(
        generate_one, range(total_personas), total=total_personas, max_workers=50
    )

    print(f"\nPersonas have been generated and saved to {output_dir}.")


if __name__ == "__main__":
    asyncio.run(main())
