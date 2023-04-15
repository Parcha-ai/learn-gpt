import asyncio
import os
import streamlit as st
import learn


openai_api_key = os.environ.get("OPENAI_API_KEY")
model = "gpt-3.5-turbo"

if st.session_state.get("openai_api_key"):
    openai_api_key = st.session_state.openai_api_key
    model = "gpt-4"


def generate_md():
    if not st.session_state.goal.strip():
        st.error("Please fill out all fields")
        return
    md = ""
    with st.spinner("Generating learning hub... "):
        st.write("(this may take up to a minute, or longer with gpt-4)")
        plan = asyncio.run(
            learn.create_plan(
                st.session_state.goal,
                model=model,
                openai_api_key=openai_api_key,
                verbose=True,
            )
        )
        md = learn.gen_plan_md(plan, model=model)
        st.session_state.plan = md


def reset():
    st.session_state.pop("plan")


if "plan" in st.session_state:
    st.button(label="Reset", on_click=reset)
    st.markdown(st.session_state.plan, unsafe_allow_html=True)
    with st.expander("Raw markdown"):
        st.code(st.session_state.plan, language="text")
else:
    with st.form(key="learn_form"):
        st.text_area(
            label="What do you want to learn? Be specific and also explain why and what your current level of knowledge is.",
            placeholder="I want to learn how to code neural networks. I want to be able to code FCN, FNN, CNNs and GANs by hand using pytorch, but also understand the math. I am an expert in python already and have a rough knowledge of linear algebra and statistics",
            key="goal",
        )
        submit = st.form_submit_button(
            label="Create learning hub", on_click=generate_md
        )
        st.divider()
        st.text_input(
            label="For gpt-4, please enter your OpenAI API key (never stored!)",
            placeholder="sk-***",
            type="password",
            key="openai_api_key",
        )
