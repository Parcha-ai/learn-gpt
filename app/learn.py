import asyncio
import json
import uuid

from pathlib import Path
from typing import Dict, List, Any
from pydantic import BaseModel, Field, parse_obj_as
from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from app import store
from app.model import Subject, Resource, Plan, Exercise
from app.util import load_malformed_json
from app.log import print_text


PROMPTS_DIR = Path(__file__).parent / "prompts"


AI_ROLE_PROMPT = PromptTemplate.from_file(
    PROMPTS_DIR / "ai_role.txt",
    ["user_goal"],
)

CREATE_TASK_PROMPT = PromptTemplate.from_file(
    PROMPTS_DIR / "create_task.txt",
    ["task", "json_response_format"],
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


class Planner(BaseModel):
    chain: LLMChain = Field(...)
    verbose: bool = False

    async def give_task(self, task: str, json_response_format: str) -> str:
        return await self.chain.arun(
            task=task,
            json_response_format=json_response_format,
            return_only_outputs=True,
        )

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
        output = await self.give_task(
            task=task,
            json_response_format=SUBJECT_LIST_RESPONSE_FORMAT,
        )
        if self.verbose:
            print("raw output:", output)
        data = load_malformed_json(output)
        if "subjects" in data:
            subject.subjects = parse_obj_as(List[Subject], data["subjects"])

    async def _ask_for_subject(self, goal: str) -> Subject:
        output = await self.give_task(
            task=ROOT_SUBJECT_TASK,
            json_response_format=SUBJECT_RESPONSE_FORMAT,
        )
        if self.verbose:
            print("raw output:", output)
        data = load_malformed_json(output)
        return Subject.parse_obj(data)

    async def _add_resources_and_exercises(self, subject: Subject, plan: Plan):
        task = f"Remember the subjects you've already been provided:\n{plan.subject.json()}\n\n"
        task += f'Generate a list of resources and exercises for the user to learn about the subject "{subject.subject}". If it does not make sense to add either resources or exercises, leave it empty.'
        output = await self.give_task(
            task=task,
            json_response_format=RESOURCES_AND_EXERCISES_FORMAT,
        )
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
        output = await self.give_task(
            task=task,
            json_response_format=ANSWER_RESPONSE_FORMAT,
        )
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
    chat = ChatOpenAI(model_name=model, openai_api_key=openai_api_key, verbose=verbose)
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=AI_ROLE_PROMPT.format(user_goal=goal)),
            HumanMessagePromptTemplate(prompt=CREATE_TASK_PROMPT),
        ]
    )

    chain = LLMChain(llm=chat, prompt=prompt, verbose=verbose)
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
