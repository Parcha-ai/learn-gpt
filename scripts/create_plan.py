import os
import asyncio

from app.learn import create_plan, get_plan_md


TEMPERATURE = 0
VERBOSE = True
# MODEL = "gpt-4"
MODEL = "gpt-3.5-turbo"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

GOAL = "I want to learn how to code neural networks. I want to be able to code FCN, FNN, CNNs and GANs by hand using pytorch, but also understand the math. I am an expert in python already and have a rough knowledge of linear algebra and statistics."
# GOAL = "I want to learn tic-tac-toe"
# GOAL = "I want to how to code a hello world in Python"


def main():
    plan = asyncio.run(
        create_plan(
            goal=GOAL, model=MODEL, openai_api_key=OPENAI_API_KEY, verbose=VERBOSE
        )
    )
    print(plan.json(indent=4))
    print(get_plan_md(plan, model=MODEL))


if __name__ == "__main__":
    main()
