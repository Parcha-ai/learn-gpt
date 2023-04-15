import asyncio
import json
import uuid

from pathlib import Path
from typing import Dict, List, Any
from pydantic import BaseModel, Field, parse_obj_as, validator
from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM
from langchain.chat_models import ChatOpenAI

import store
from model import Subject, Resource, Plan, Exercise
from util import fix_json, load_malformed_json


PROMPTS_DIR = Path(__file__).parent

JSON_TASK_PROMPT = PromptTemplate.from_file(
    PROMPTS_DIR / "prompt.txt",
    ["ai_role", "user_goal", "ai_task", "constraints", "json_response_format"],
)


def format_numbered_list(items: List[str]):
    return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])


AI_ROLE = "You are a professor and a tutor. Your role is to create a custom curriculum and course for your user to achieve a goal. Your decisions must always be made independently without seeking user assistance. Play to your strengths as an LLM and pursue simple strategies with no legal complications."
CONSTRAINTS = format_numbered_list(
    [
        "~4000 word limit for short term memory. Your short term memory is short, so immediately save important information to files.",
        "No user assistance",
        'Refer to the user in the second person as "you"',
    ]
)

SUBJECTS_AND_TOPICS = "subjects/topics"
RESOURCES_AND_EXERCISES = "resources/exercises"

ANSWER_JSON = {
    "answer": "answer",
}
ANSWER_RESPONSE_FORMAT = json.dumps(ANSWER_JSON, indent=4)
SUBJECT_JSON = {
    "subject": "subject",
    "description": "description",
    "reason": "reason",
}
SUBJECT_RESPONSE_FORMAT = json.dumps(SUBJECT_JSON, indent=4)
SUBJECT_LIST_RESPONSE_FORMAT = json.dumps(
    {"subjects": [SUBJECT_JSON]},
    indent=4,
)
RESOURCES_AND_EXERCISES_FORMAT = """{
    "resources": [
        {
            "title": "resource title",
            "description": "resource description"
        }
    ],
    "exercises": [
        {
          "description": "exercise description"
        }
    ]
}
"""
ROOT_SUBJECT_TASK = (
    "Provide exactly one subject title based on what the user wants to learn."
)
GEN_SUBJECTS_TASK = "Provide a list of subjects that the user should learn in order to achieve the above goal along with a description of the subject and reason why that subject is important."


class SimpleChain(LLMChain):
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False) -> LLMChain:
        template = "{prompt}"
        pt = PromptTemplate(
            template=template,
            input_variables=[
                "prompt",
            ],
        )
        return cls(prompt=pt, llm=llm, verbose=verbose)


def create_json_prompt(goal: str, task: str, response_format: str) -> str:
    prompt = JSON_TASK_PROMPT.format(
        ai_role=AI_ROLE,
        user_goal=goal,
        ai_task=task,
        constraints=CONSTRAINTS,
        json_response_format=response_format,
    )
    return prompt


class Planner(BaseModel):
    chain: SimpleChain = Field(...)
    verbose: bool = False

    async def generate(self, goal: str) -> Plan:
        subject = await self._ask_for_subject(goal=goal)
        plan = Plan(goal=goal, subject=subject)
        await self._process_subject(subject=plan.subject, plan=plan, depth=1)
        return plan

    async def _process_subject(self, subject: Subject, plan: Plan, depth: int):
        answer = ""
        if depth < 3:
            question = f'For the user to learn about the subject "{subject.subject}" is this subject large or important enough to be broken down into discrete topics or should the user go straight to resources and exercises? Answer with either "topics" or "{RESOURCES_AND_EXERCISES}" below'
            answer = await self._ask_for_answer(question=question, plan=plan)

        if answer == "topics":
            await self._add_subjects_and_topics(subject=subject, plan=plan)
            tasks = []
            for child_subject in subject.subjects:
                task = asyncio.create_task(
                    self._process_subject(
                        subject=child_subject,
                        plan=plan,
                        depth=depth + 1,
                    )
                )
                tasks.append(task)
            await asyncio.gather(*tasks)
        else:
            await self._add_resources_and_exercises(subject=subject, plan=plan)

    async def _add_subjects_and_topics(self, subject: Subject, plan: Plan):
        task = f"Remember the subjects you've already been provided:\n{plan.subject.json()}\n\n"
        task += f'Provide a list of subjects (sub-topics) related to "{subject.subject}" that the user should learn in order to achieve the above goal along with a description of the topic and reason why that topic is important.'
        prompt = create_json_prompt(
            goal=plan.goal, task=task, response_format=SUBJECT_LIST_RESPONSE_FORMAT
        )
        output = await self.chain.arun(prompt=prompt, return_only_outputs=True)
        if self.verbose:
            print("raw output:", output)
        data = load_malformed_json(output)
        if "subjects" in data:
            subject.subjects = parse_obj_as(List[Subject], data["subjects"])

    async def _ask_for_subject(self, goal: str) -> Subject:
        prompt = create_json_prompt(
            goal=goal, task=ROOT_SUBJECT_TASK, response_format=SUBJECT_RESPONSE_FORMAT
        )
        output = await self.chain.arun(prompt=prompt, return_only_outputs=True)
        if self.verbose:
            print("raw output:", output)
        data = load_malformed_json(output)
        return Subject.parse_obj(data)

    async def _add_resources_and_exercises(self, subject: Subject, plan: Plan):
        task = f"Remember the subjects you've already been provided:\n{plan.subject.json()}\n\n"
        task += f'Generate a list of resources and exercises for the user to learn about the subject "{subject.subject}". If it does not make sense to add either resources or exercises, leave it empty.'
        prompt = create_json_prompt(
            goal=plan.goal, task=task, response_format=RESOURCES_AND_EXERCISES_FORMAT
        )
        output = await self.chain.arun(prompt=prompt, return_only_outputs=True)
        if self.verbose:
            print("raw output:", output)
        data = load_malformed_json(output)
        if "resources" in data:
            subject.resources = parse_obj_as(List[Resource], data["resources"])
        if "exercises" in data:
            subject.exercises = parse_obj_as(List[Exercise], data["exercises"])

    async def _ask_for_answer(self, question: str, plan: Plan) -> str:
        task = f"Remember the subjects you've already been provided:\n{plan.subject.json()}\n"
        task += question
        prompt = create_json_prompt(
            goal=plan.goal, task=task, response_format=ANSWER_RESPONSE_FORMAT
        )
        output = await self.chain.arun(prompt=prompt, return_only_outputs=True)
        if self.verbose:
            print("raw output:", output)
        data = load_malformed_json(output)
        return data["answer"]


async def create_plan(
    goal: str,
    model: str,
    openai_api_key,
    verbose: bool,
) -> Plan:
    llm = ChatOpenAI(model_name=model, openai_api_key=openai_api_key, verbose=verbose)
    chain = SimpleChain.from_llm(llm, verbose=verbose)
    planner = Planner(chain=chain, verbose=verbose)
    plan = await planner.generate(goal=goal)
    store.save_plan(plan)
    return plan


def sanitize_anchor_name(name):
    return name.lower().replace(" ", "-")


def get_link_md(name, label=None):
    label = label or name
    return f"[{label}](#{sanitize_anchor_name(name)})"


def get_href(name):
    return f"<a id='{sanitize_anchor_name(name)}'></a>"


def get_toc_md(subject: Subject, level: int) -> str:
    indent = "  " * level
    content = f"{indent} * {get_link_md(subject.subject)}\n"
    if subject.subjects:
        for child_subject in subject.subjects:
            content += get_toc_md(child_subject, level + 1)
    return content


def get_subject_md(subject: Subject, level: int) -> str:
    header_prefix = "#" * level
    anchor = get_href(subject.subject)
    content = f"{header_prefix} {subject.subject}{anchor}\n"
    content += f"{subject.description}\n\n"
    content += f"{subject.reason}\n\n"
    if subject.subjects:
        for child_subject in subject.subjects:
            content += get_subject_md(child_subject, level + 1)
    if subject.resources:
        anchor = get_href(subject.subject + "_resources")
        content += f"{header_prefix}# Resources{anchor}\n"
        for resource in subject.resources:
            content += f"* {resource.title}: {resource.description}\n"
    if subject.exercises:
        anchor = get_href(subject.subject + "_exercises")
        content += f"{header_prefix}# Exercises{anchor}\n"
        for exercise in subject.exercises:
            content += f"* {exercise.description}\n"
    return content


def get_plan_md(plan: Plan, model: str) -> str:
    root = plan.subject
    content = f"# Learning Hub: {root.subject}\n"
    content += f"(generated with {model})\n\n"
    content += f"> {plan.goal}\n\n"
    content += f"{get_toc_md(subject=root, level=0)}\n\n"
    content += get_subject_md(subject=root, level=1)
    return content.strip() + "\n"


def fake_plan() -> Plan:
    with open("examples/nn_plan.json", "r") as f:
        return Plan.parse_raw(f.read())
