import os
import json

from typing import Dict, List
from quart import Quart, request, jsonify
from learn import create_plan, fake_plan

app = Quart(__name__)

DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def bad_request(message: str):
    return jsonify({"error": message}), 400


@app.route("/v1/create_plan", methods=["POST"])
async def create_plan():
    data = await request.json
    if data.get("fake", False):
        return jsonify({"plan": json.loads(fake_plan().json())})
    goal = data.get("goal")
    if not goal:
        return bad_request("goal not provided")
    openai_api_key = data.get("openai_api_key", DEFAULT_OPENAI_API_KEY)
    model = data.get("model", DEFAULT_MODEL)
    plan = create_plan(
        goal=goal, model=model, openai_api_key=openai_api_key, verbose=True
    )
    return jsonify({"plan": json.loads(plan.json())})


@app.after_request
def add_header(r):
    # for development
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
