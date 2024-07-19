import json
import pathlib
from abc import ABC, abstractmethod

import openai


class BasePolicy(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def forward(observation, available_actions):
        """
        Args:
            observation (`str`):
                HTML string

            available_actions ():
                ...
        Returns:
            action (`str`):
                Return string of the format ``action_name[action_arg]''.
                Examples:
                    - search[white shoes]
                    - click[button=Reviews]
                    - click[button=Buy Now]
        """
        raise NotImplementedError


class OpenAIPolicy(BasePolicy):
    def __init__(self, persona, intent):
        super().__init__()
        self.client = openai.Client()
        self.short_term_memory = []
        self.previous_actions = []
        self.plan = "EMPTY"
        self.persona = persona
        self.intent = intent
        self.prompt = open(pathlib.Path(__file__).parent / "openai_prompt.txt").read(
            10000000
        )

    def forward(self, observation, available_actions):
        this_turn_prompt = f"""
### current plan: {self.plan}
### persona: {self.persona}
### intent: {self.intent}
### memories:
{self.short_term_memory}
### previous actions:
{self.previous_actions}
### current webpage:
{observation['page']}
### current url:
{observation['url']}
### clickable items in the webpage:
{observation['clickables']}
"""
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": this_turn_prompt},
            ],
            max_tokens=1000,
            response_format={"type": "json_object"},
        )
        output = response.choices[0].message.content
        print(output)
        output = json.loads(output)
        if "current_plan" in output:
            self.plan = output["current_plan"]
        if "new_memories" in output:
            self.short_term_memory += output["new_memories"]
        self.previous_actions.append(output["action"])

        return json.dumps(output["action"])


class HumanPolicy(BasePolicy):
    def __init__(self):
        super().__init__()

    def forward(self, observation, available_actions):
        action = input("> ")
        try:
            action, param = action.split(" ", 1)
            if param.strip():
                # change a=b,c=d to dict
                param = {a.split("=")[0]: a.split("=")[1] for a in param.split(",")}
            else:
                param = {}
        except Exception as e:
            print(e)
            print("try again")
            return self.forward(observation, available_actions)
        return json.dumps({"type": action, **param})
