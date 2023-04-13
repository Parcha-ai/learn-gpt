import os
import streamlit as st
import learn


openai_api_key = os.environ.get("OPENAI_API_KEY")
model = "gpt-3.5-turbo"

if st.session_state.get("openai_api_key"):
    openai_api_key = st.session_state.openai_api_key
    model = "gpt-4"

chain = learn.ProfessorGPT.build(model=model, openai_api_key=openai_api_key)


def generate_md():
    if (
        not st.session_state.goal.strip()
        and not st.session_state.reason.strip()
        and not st.session_state.knowledge.strip()
    ):
        st.error("Please fill out all fields")
        return
    md = ""
    with st.spinner("Generating learning hub... "):
        st.write("(this may take up to a minute, or longer with gpt-4)")
        out = chain(
            {
                "goal": st.session_state.goal,
                "reason": st.session_state.reason,
                "knowledge": st.session_state.knowledge,
            }
        )
        md = out.get("markdown", None)
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
        st.text_input(
            label="What do you want to learn?",
            placeholder="I want to learn how to golf",
            key="goal",
        )
        st.text_input(
            label="Why do you want to learn this?",
            placeholder="To play with my friends on the weekends",
            key="reason",
        )
        st.text_input(
            label="What is your current level of knowledge?",
            placeholder="I've played mini golf",
            key="knowledge",
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
