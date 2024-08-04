import datetime
import json
import logging
import pathlib
import pickle
import time
import uuid
from abc import ABC, abstractmethod

import openai

from ..agent import Agent

logger = logging.getLogger(__name__)


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


class AgentPolicy(BasePolicy):
    def __init__(self, persona, intent):
        logger.info(f"Creating AgentPolicy with persona: {persona}, intent: {intent}")
        self.agent = Agent(persona, intent)
        self.agent.add_thought(f"I want to {intent}")
        # lets' have a run name with current time and random string to save agent checkpoints
        # 2024-02-02_05:05:05
        self.run_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}_{uuid.uuid4().hex[:4]}"
        self.run_path = pathlib.Path() / "runs" / self.run_name
        self.run_path.mkdir(parents=True)
        (self.run_path / "persona.txt").write_text(persona)
        (self.run_path / "intent.txt").write_text(intent)
        self.action_trace_file = (self.run_path / "action_trace.txt").open("w")
        self.env_trace_file = (self.run_path / "env_trace.txt").open("w")

    def forward(self, observation, available_actions):
        self.env_trace_file.write(json.dumps(observation) + "\n")
        self.agent.perceive(observation)
        self.agent.reflect()
        self.agent.wonder()
        self.agent.plan()
        action = self.agent.act(observation)
        pickle.dump(
            self.agent,
            open(self.run_path / f"agent_{self.agent.memory.timestamp}.pkl", "wb"),
        )
        (self.run_path / f"memory_trace_{self.agent.memory.timestamp}.txt").write_text(
            "\n".join(self.agent.format_memories(self.agent.memory.memories))
        )
        (self.run_path / f"page_{self.agent.memory.timestamp}.html").write_text(
            observation["page"]
        )
        self.agent.memory.timestamp += 1
        self.action_trace_file.write(json.dumps(action) + "\n")
        self.action_trace_file.flush()
        self.env_trace_file.flush()
        return json.dumps(action)
