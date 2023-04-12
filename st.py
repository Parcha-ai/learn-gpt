import streamlit as st
import learn


chain = learn.ProfessorGPT.build()


def generate_md():
    md = ""
    with st.spinner("Generating learning hub... (this may take up to a minute)"):
        # out = chain(
        #     {
        #         "goal": st.session_state.goal,
        #         "reason": st.session_state.reason,
        #         "knowledge": st.session_state.knowledge,
        #     }
        # )
        # md = out.get("markdown", None)
        st.session_state.plan = "# hello"


def reset():
    st.session_state.pop("plan")


if "plan" in st.session_state:
    st.button(label="Reset", on_click=reset)
    st.markdown(st.session_state.plan, unsafe_allow_html=True)
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
