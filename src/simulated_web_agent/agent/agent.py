import asyncio
import json
import logging

from .gpt import async_chat, load_prompt
from .memory import (Action, Memory, MemoryPiece, Observation, Plan,
                     Reflection, Thought)

PERCEIVE_PROMPT = load_prompt("perceive")
REFLECT_QUESTION_PROMPT = load_prompt("reflect_question")
REFLECT_ANSWER_PROMPT = load_prompt("reflect_answer")
REFLECT_IMPORTANCE_PROMPT = load_prompt("reflect_importance")
WONDER_PROMPT = load_prompt("wonder")
PLANNING_PROMPT = load_prompt("planning")
EVALUATE_PLAN_PROMPT = load_prompt("evaluate_plan")
ACTION_PROMPT = load_prompt("action")
FEEDBACK_PROMPT = load_prompt("feedback")
logger = logging.getLogger(__name__)


class Agent:
    memory: Memory
    persona: str
    current_plan: MemoryPiece

    def __init__(self, persona, intent):
        self.memory = Memory()
        self.persona = persona
        self.intent = intent
        self.current_plan = None

    async def perceive(self, environment):
        environment = json.dumps(environment)
        logger.info("agent preceiving environment ...")
        observasions = await async_chat(
            [
                {"role": "system", "content": PERCEIVE_PROMPT},
                {"role": "user", "content": environment},
            ],
            response_format={"type": "json_object"},
        )
        logger.info("Perceived: %s", observasions.choices[0].message.content)
        observasions = json.loads(observasions.choices[0].message.content)
        observasions = observasions["observations"]
        for o in observasions:
            Observation(o, self.memory, environment)

    @staticmethod
    def format_memories(memories: list[MemoryPiece]):
        memories = [
            f"""timestamp: {m.timestamp}; kind: {m.kind}; importance: {m.importance:.2f}, content: {m.content}"""
            for m in memories
        ]
        return memories

    async def feedback(self, obs):
        last_action = None
        last_plan = self.current_plan
        for m in self.memory.memories[::-1]:
            if isinstance(m, Action):
                last_action = m
                break
        resp = await async_chat(
            [
                {"role": "system", "content": FEEDBACK_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "persona": self.persona,
                            "last_action": last_action.raw_action,
                            "last_plan": last_plan.content,
                            "observation": obs,
                        }
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        resp = json.loads(resp.choices[0].message.content)
        logger.info("feedback: %s", resp)
        for thought in resp["thoughts"]:
            Thought(thought, self.memory)

    async def reflect(self):
        # we reflect on the most recent memories
        # two most recent memories (last observasion, reflect, plan, action)
        logger.info("reflecting on memories ...")
        memories = [
            i for i in self.memory.memories if i.timestamp >= self.memory.timestamp - 1
        ]
        memories = self.format_memories(memories)
        model_input = {
            "current_timestamp": self.memory.timestamp,
            "memories": memories,
        }
        questions = await async_chat(
            [
                {"role": "system", "content": REFLECT_QUESTION_PROMPT},
                {"role": "user", "content": "Your Persona: " + self.persona},
                {"role": "user", "content": json.dumps(model_input)},
            ],
            response_format={"type": "json_object"},
        )
        questions = json.loads(questions.choices[0].message.content)["questions"]
        logger.info(
            f"reflecting on {questions}",
        )
        reflections = []
        answers = []
        # for q in questions:
        #     memories = self.memory.retrieve(q)
        #     memories = self.format_memories(memories)
        #     answer = chat(
        #         [
        #             {"role": "system", "content": REFLECT_ANSWER_PROMPT},
        #             {"role": "user", "content": "Your Persona: " + self.persona},
        #             {
        #                 "role": "user",
        #                 "content": json.dumps(
        #                     {
        #                         "question": q,
        #                         "memories": memories,
        #                     }
        #                 ),
        #             },
        #         ],
        #         response_format={"type": "json_object"},
        #     )
        #     answer = json.loads(answer.choices[0].message.content)
        #     if answer["answer"] == "N/A":
        #         continue
        #     answers.append(answer)
        # make parallel requests
        requests = [
            [
                {
                    "role": "system",
                    "content": REFLECT_ANSWER_PROMPT,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "question": q,
                            "memories": self.format_memories(self.memory.retrieve(q)),
                        }
                    ),
                },
            ]
            for q in questions
        ]
        results = await asyncio.gather(*[async_chat(r, response_format={"type": "json_object"},) for r in requests])
        for answer in results:
            if answer.choices[0].message.content == "N/A":
                continue
            answers.append(json.loads(answer.choices[0].message.content))
        try:
            for answer in answers:
                reflections.append(
                    Reflection(
                        answer["answer"],
                        self.memory,
                        [memories[i] for i in answer["target"]],
                    )
                )
        except IndexError as e:
            logger.error("Reflection failed: %s", e)
            Thought("Reflection failed", self.memory)
        # now get importance
        requests = [
            [
                {
                    "role": "system",
                    "content": REFLECT_IMPORTANCE_PROMPT,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "answer": r.content,
                            "persona": self.persona,
                            "intent": self.intent,
                        }
                    ),
                },
            ]
            for r in reflections
        ]
        if len(requests) == 0:
            return
        responses = await asyncio.gather(*[async_chat(r, response_format={"type": "json_object"}) for r in requests])
        importance = [
            json.loads(r.choices[0].message.content)["importance_score"]
            for r in responses
        ]
        for r, i in zip(reflections, importance):
            r.importance = i / 10

    async def wonder(self):
        logger.info("wondering ...")
        memories = self.memory.memories[-50:]  # get the last 50 memories
        memories = self.format_memories(memories)
        resp = await async_chat(
            [
                {"role": "system", "content": WONDER_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "persona": self.persona,
                            "memories": memories,
                            "intent": self.intent,
                        }
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        resp = json.loads(resp.choices[0].message.content)
        logger.info("wondering: %s", resp)
        for thought in resp["thoughts"]:
            Thought(thought, self.memory)

    async def plan(self):
        logger.info("planning ...")
        memories = self.memory.retrieve(
            self.intent, include_recent_observation=True, include_recent_action=True
        )
        memories = self.format_memories(memories)
        new_plan = ""
        rationale = ""
        while True:
            resp = await async_chat(
                [
                    {
                        "role": "system",
                        "content": PLANNING_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "persona": self.persona,
                                "intent": self.intent,
                                "memories": memories,
                                "current_timestamp": self.memory.timestamp,
                                "old_plan": "N/A"
                                if self.current_plan is None
                                else self.current_plan.content,
                            }
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                model="gpt-4-turbo",
            )
            # # print(resp.choices[0].message.content)
            resp = resp.choices[0].message.content
            if "plan" in json.loads(resp) and "rationale" in json.loads(resp):
                new_plan = json.loads(resp)["plan"]
                rationale = json.loads(resp)["rationale"] if "rationale" in json.loads(resp) else "N/A"
                # make sure they are str
                if type(new_plan) == str and type(rationale) == str:
                    break
            logger.info("invalid response, rethinking... ")
        logger.info("plan: %s", new_plan)
        logger.info("rationale: %s", rationale)
        self.current_plan = Plan(new_plan, self.memory)
        Thought(rationale, self.memory)

    async def act(self, env):
        memories = self.memory.retrieve(self.intent, include_recent_action=True)
        memories = self.format_memories(memories)
        action = await async_chat(
            [
                {"role": "system", "content": ACTION_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "persona": self.persona,
                            "intent": self.intent,
                            "plan": self.current_plan.content,
                            "environment": env,
                            "recent_memories": memories,
                        }
                    ),
                },
            ],
            response_format={"type": "json_object"},
            model="gpt-4o",
        )
        action = json.loads(action.choices[0].message.content)
        Action(action["description"], self.memory, json.dumps(action))
        return action

    def add_thought(self, thought):
        Thought(thought, self.memory)
