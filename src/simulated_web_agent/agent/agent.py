import asyncio
import inspect
import json
import logging
import time
from typing import Optional, Union

from . import context
from .gpt import async_chat, load_prompt
from .memory import Action, Memory, MemoryPiece, Observation, Plan, Reflection, Thought

PERCEIVE_PROMPT = load_prompt("perceive")
REFLECT_PROMPT = load_prompt("reflect")
REFLECT_ANSWER_PROMPT = load_prompt("reflect_answer")
REFLECT_IMPORTANCE_PROMPT = load_prompt("reflect_importance")
WONDER_PROMPT = load_prompt("wonder")
PLANNING_PROMPT = load_prompt("planning")
EVALUATE_PLAN_PROMPT = load_prompt("evaluate_plan")
ACTION_PROMPT = load_prompt("action")
FEEDBACK_PROMPT = load_prompt("feedback")
logger = logging.getLogger(__name__)


# context manager to log api calls
class LogApiCall:
    def __enter__(self):
        Agent.api_call_count += 1
        logger.info("API call count: %s", Agent.api_call_count)
        self.method_name = inspect.currentframe().f_back.f_code.co_name
        self.retrieve_result = []
        self.request = []
        self.response = []
        self.start_time = time.time()
        context.api_call_manager = self

    def __exit__(self, exc_type, exc_value, traceback):
        context.api_call_manager = None
        with open(
            context.run_path / f"api_trace_{Agent.api_call_count}.json", "w"
        ) as f:
            json.dump(
                {
                    "request": self.request,
                    "response": self.response,
                    "method_name": self.method_name,
                    "retrieve_result": self.retrieve_result,
                    "time": time.time() - self.start_time,
                },
                f,
            )


class Agent:
    memory: Memory
    persona: str
    current_plan: Optional[Plan]
    last_reflect_index = 0
    api_call_count = 0

    def __init__(self, persona, intent):
        self.memory = Memory(self)
        self.persona = persona
        self.intent = intent
        self.current_plan = None

    async def perceive(self, environment):
        # environment = json.dumps(environment)
        pages = environment["page"].split("<split-marker/>")
        envs = [
            {
                **environment,
                "page": p,
            }
            for p in pages
        ]
        envs = [json.dumps(e) for e in envs]
        logger.info("agent perceiving environment ...")
        observasions = []
        with LogApiCall():
            requests = [
                [
                    {"role": "system", "content": PERCEIVE_PROMPT},
                    {"role": "user", "content": e},
                ]
                for e in envs
            ]
            results = await asyncio.gather(
                *[
                    async_chat(r, response_format={"type": "json_object"})
                    for r in requests
                ]
            )
            # logger.info("Perceived: %s", observasions.choices[0].message.content)
            # observasions = json.loads(observasions.choices[0].message.content)
            for r in results:
                logger.info("Perceived: %s", r.choices[0].message.content)
                observasions += json.loads(r.choices[0].message.content)["observations"]
            #  = await async_chat(
            #     [
            #         {"role": "system", "content": PERCEIVE_PROMPT},
            #         {"role": "user", "content": environment},
            #     ],
            #     response_format={"type": "json_object"},
            # )

        # observasions = observasions["observations"]
        for o in observasions:
            await self.memory.add_memory_piece(Observation(o, self.memory, environment))

    @staticmethod
    def format_memories(memories: list[MemoryPiece], sort_by_kind=True) -> list[str]:
        # sort by kind and timestamp
        if sort_by_kind:
            memories = sorted(memories, key=lambda x: (x.kind, x.timestamp))
        importances_str = [
            f"{m.importance:.2f}" if m.importance != -1 else "N/A" for m in memories
        ]
        memories_str = [
            f"""timestamp: {m.timestamp}; kind: {m.kind}; importance: {i}, content: {m.content}"""
            for m, i in zip(memories, importances_str)
        ]
        return memories_str

    async def feedback(self, obs):
        last_action = None
        last_plan = self.current_plan
        for m in self.memory.memories[::-1]:
            if isinstance(m, Action):
                last_action = m
                break
        assert last_action is not None
        assert last_plan is not None
        with LogApiCall():
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
            await self.memory.add_memory_piece(Thought(thought, self.memory))

    async def reflect(self):
        # we reflect on the most recent memories
        # two most recent memories (last observasion, reflect, plan, action)
        logger.info("reflecting on memories ...")
        # memories = [
        #     i for i in self.memory.memories if i.timestamp >= self.memory.timestamp - 1
        # ]
        memories = self.memory.memories[self.last_reflect_index :]
        self.last_reflect_index = len(self.memory.memories)
        memories = self.format_memories(memories)
        model_input = {
            "current_timestamp": self.memory.timestamp,
            "memories": memories,
            "persona": self.persona,
        }
        # with LogApiCall():
        reflections = await async_chat(
            [
                {"role": "system", "content": REFLECT_PROMPT},
                {"role": "user", "content": json.dumps(model_input)},
            ],
            response_format={"type": "json_object"},
            log=False,
            model="gpt-4-turbo",
        )
        reflections = json.loads(reflections.choices[0].message.content)["insights"]
        logger.info("reflections: %s", reflections)
        for r in reflections:
            await self.memory.add_memory_piece(Reflection(r, self.memory))
        # todo

        # logger.info(
        #     f"reflecting on {questions}",
        # )
        # reflections = []
        # answers = []
        # requests = [
        #     [
        #         {
        #             "role": "system",
        #             "content": REFLECT_ANSWER_PROMPT,
        #         },
        #         {
        #             "role": "user",
        #             "content": json.dumps(
        #                 {
        #                     "question": q,
        #                     "memories": self.format_memories(
        #                         await self.memory.retrieve(q)
        #                     ),
        #                 }
        #             ),
        #         },
        #     ]
        #     for q in questions
        # ]
        # results = await asyncio.gather(
        #     *[
        #         async_chat(
        #             r,
        #             response_format={"type": "json_object"},
        #         )
        #         for r in requests
        #     ]
        # )
        # for answer in results:
        #     answer = json.loads(answer.choices[0].message.content)
        #     if answer["answer"] != "N/A":
        #         answers.append(answer)
        # try:
        #     for answer in answers:
        #         reflections.append(
        #             Reflection(
        #                 answer["answer"],
        #                 self.memory,
        #                 [memories[i] for i in answer["target"]],
        #             )
        #         )
        # except IndexError as e:
        #     logger.error("Reflection failed: %s", e)
        #     await self.memory.add_memory_piece(
        #         Thought("Reflection failed", self.memory)
        #     )

    async def wonder(self):
        logger.info("wondering ...")
        memories = self.memory.memories[-50:]  # get the last 50 memories
        memories = self.format_memories(memories)
        # with LogApiCall():
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
            log=False,
            response_format={"type": "json_object"},
        )
        resp = json.loads(resp.choices[0].message.content)
        logger.info("wondering: %s", resp)
        for thought in resp["thoughts"]:
            await self.memory.add_memory_piece(Thought(thought, self.memory))

    async def plan(self):
        logger.info("planning ...")
        with LogApiCall():
            memories = await self.memory.retrieve(
                self.intent,
                include_recent_observation=True,
                trigger_update=False,
                kind_weight={"action": 10, "plan": 10, "thought": 10, "reflection": 10},
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
                    model="gpt-4o",
                )
                # # print(resp.choices[0].message.content)
                resp = resp.choices[0].message.content
                resp = json.loads(resp)
                if "plan" in resp and "rationale" in resp and "next_step" in resp:
                    logger.info(
                        "retrieved memory for planning: %s", "\n".join(memories)
                    )
                    new_plan = resp["plan"]
                    rationale = resp["rationale"] if "rationale" in resp else "N/A"
                    next_step = resp["next_step"]
                    # make sure they are str
                    if type(new_plan) == str and type(rationale) == str:
                        break
                logger.info("invalid response, rethinking... ")
                logger.info("response: %s", resp)
        logger.info("plan: %s", new_plan)
        logger.info("rationale: %s", rationale)
        logger.info("next_step: %s", next_step)
        self.current_plan = Plan(new_plan, self.memory, next_step)
        await self.memory.add_memory_piece(Thought(rationale, self.memory))

    async def act(self, env):
        with LogApiCall():
            memories = await self.memory.retrieve(
                self.current_plan.next_step,
                trigger_update=False,
                kind_weight={"observation": 0, "action": 10, "thought": 10},
            )
            memories = self.format_memories(memories)
            assert self.current_plan is not None
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
                                "next_step": self.current_plan.next_step,
                                "environment": env,
                                "recent_memories": memories,
                            }
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                model="gpt-4o",
            )
        actions = json.loads(action.choices[0].message.content)
        logger.info("actions: %s", actions)
        for action in actions["actions"]:
            await self.memory.add_memory_piece(
                Action(action["description"], self.memory, json.dumps(action))
            )

        return actions["actions"]

    async def add_thought(self, thought):
        await self.memory.add_memory_piece(Thought(thought, self.memory))
