import asyncio
import json
import os

from util import fix_json, load_malformed_json
from pathlib import Path
from typing import Dict, List, Any
from pydantic import BaseModel, parse_obj_as
from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM
from langchain.chat_models import ChatOpenAI


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


class Resource(BaseModel):
    title: str
    description: str


class Exercise(BaseModel):
    description: str


class Subject(BaseModel):
    subject: str
    description: str = ""
    reason: str = ""
    subjects: List["Subject"] = []
    resources: List[Resource] = []
    exercises: List[Exercise] = []


class Plan(BaseModel):
    goal: str
    subject: Subject


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


async def ask_for_answer(chain: SimpleChain, question: str, plan: Plan) -> str:
    task = (
        f"Remember the subjects you've already been provided:\n{plan.subject.json()}\n"
    )
    task += question
    prompt = create_json_prompt(
        goal=plan.goal, task=task, response_format=ANSWER_RESPONSE_FORMAT
    )
    output = await chain.arun(prompt=prompt, return_only_outputs=True)
    if VERBOSE:
        print("raw output:", output)
    data = load_malformed_json(output)
    return data["answer"]


async def ask_for_subject(chain: SimpleChain, goal: str) -> Subject:
    prompt = create_json_prompt(
        goal=goal, task=ROOT_SUBJECT_TASK, response_format=SUBJECT_RESPONSE_FORMAT
    )
    output = await chain.arun(prompt=prompt, return_only_outputs=True)
    if VERBOSE:
        print("raw output:", output)
    output = fix_json(output)
    return Subject.parse_raw(output)


async def add_subjects_and_topics(chain: SimpleChain, subject: Subject, plan: Plan):
    task = f"Remember the subjects you've already been provided:\n{plan.subject.json()}\n\n"
    task += f'Provide a list of subjects (sub-topics) related to "{subject.subject}" that the user should learn in order to achieve the above goal along with a description of the topic and reason why that topic is important.'
    prompt = create_json_prompt(
        goal=plan.goal, task=task, response_format=SUBJECT_LIST_RESPONSE_FORMAT
    )
    output = await chain.arun(prompt=prompt, return_only_outputs=True)
    if VERBOSE:
        print("raw output:", output)
    data = load_malformed_json(output)
    if "subjects" in data:
        subject.subjects = parse_obj_as(List[Subject], data["subjects"])


async def add_resources_and_exercises(chain: SimpleChain, subject: Subject, plan: Plan):
    task = f"Remember the subjects you've already been provided:\n{plan.subject.json()}\n\n"
    task += f'Generate a list of resources and exercises for the user to learn about the subject "{subject.subject}". If it does not make sense to add either resources or exercises, leave it empty.'
    prompt = create_json_prompt(
        goal=plan.goal, task=task, response_format=RESOURCES_AND_EXERCISES_FORMAT
    )
    output = await chain.arun(prompt=prompt, return_only_outputs=True)
    if VERBOSE:
        print("raw output:", output)
    data = load_malformed_json(output)
    if "resources" in data:
        subject.resources = parse_obj_as(List[Resource], data["resources"])
    if "exercises" in data:
        subject.exercises = parse_obj_as(List[Exercise], data["exercises"])


async def process_subject(chain: SimpleChain, subject: Subject, plan: Plan, depth: int):
    answer = ""
    if depth < 3:
        question = f'For the user to learn about the subject "{subject.subject}" is this subject large or important enough to be broken down into discrete topics or should the user go straight to resources and exercises? Answer with either "topics" or "{RESOURCES_AND_EXERCISES}" below'
        answer = await ask_for_answer(chain, question=question, plan=plan)

    if answer == "topics":
        await add_subjects_and_topics(chain, subject=subject, plan=plan)
        tasks = []
        for child_subject in subject.subjects:
            task = asyncio.create_task(
                process_subject(
                    chain=chain,
                    subject=child_subject,
                    plan=plan,
                    depth=depth + 1,
                )
            )
            tasks.append(task)
        await asyncio.gather(*tasks)
    else:
        await add_resources_and_exercises(chain, subject=subject, plan=plan)


async def generate_full_plan(chain: SimpleChain, goal: str) -> Plan:
    subject = await ask_for_subject(chain=chain, goal=goal)
    plan = Plan(goal=goal, subject=subject)
    await process_subject(chain=chain, subject=plan.subject, plan=plan, depth=1)
    return plan


def gen_anchor(name):
    return name.lower().replace(" ", "-")


def gen_md_link(name, label=None):
    label = label or name
    return f"[{label}](#{gen_anchor(name)})"


def gen_href(name):
    return f"<a id='{gen_anchor(name)}'></a>"


def gen_toc_md(subject: Subject, level: int) -> str:
    indent = "  " * level
    content = f"{indent} * {gen_md_link(subject.subject)}\n"
    if subject.subjects:
        for child_subject in subject.subjects:
            content += gen_toc_md(child_subject, level + 1)
    return content


def gen_subject_md(subject: Subject, level: int) -> str:
    header_prefix = "#" * level
    anchor = gen_href(subject.subject)
    content = f"{header_prefix} {subject.subject}{anchor}\n"
    content += f"{subject.description}\n\n"
    content += f"{subject.reason}\n\n"
    if subject.subjects:
        for child_subject in subject.subjects:
            content += gen_subject_md(child_subject, level + 1)
    if subject.resources:
        anchor = gen_href(subject.subject + "_resources")
        content += f"{header_prefix}# Resources{anchor}\n"
        for resource in subject.resources:
            content += f"* {resource.title}: {resource.description}\n"
    if subject.exercises:
        anchor = gen_href(subject.subject + "_exercises")
        content += f"{header_prefix}# Exercises{anchor}\n"
        for exercise in subject.exercises:
            content += f"* {exercise.description}\n"
    return content


def gen_plan_md(plan: Plan, model: str):
    root = plan.subject
    content = f"# Learning Hub: {root.subject}\n"
    content += f"(generated with {model})\n\n"
    content += f"> {plan.goal}\n\n"
    content += f"{gen_toc_md(subject=root, level=0)}\n\n"
    content += gen_subject_md(subject=root, level=1)
    return content.strip() + "\n"


async def create_plan(
    goal: str,
    model: str,
    openai_api_key,
    verbose: bool,
) -> str:
    llm = ChatOpenAI(model_name=model, openai_api_key=openai_api_key, verbose=verbose)
    chain = SimpleChain.from_llm(llm, verbose=verbose)
    return await generate_full_plan(chain, goal=goal)


def fake_plan() -> Plan:
    with open("examples/nn_plan.json", "r") as f:
        return Plan.parse_raw(f.read())


TEMPERATURE = 0
VERBOSE = True
# MODEL = "gpt-4"
MODEL = "gpt-3.5-turbo"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# GOAL = "I want to learn how to code neural networks. I want to be able to code FCN, FNN, CNNs and GANs by hand using pytorch, but also understand the math. I am an expert in python already and have a rough knowledge of linear algebra and statistics."
# GOAL = "I want to learn tic-tac-toe"
GOAL = "I want to how to code a hello world in Python"


def main():
    plan = asyncio.run(
        create_plan(
            goal=GOAL, model=MODEL, openai_api_key=OPENAI_API_KEY, verbose=VERBOSE
        )
    )
    print(plan.json(indent=4))
    print(gen_plan_md(plan, model=MODEL))


if __name__ == "__main__":
    main()
