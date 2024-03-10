import streamlit as st
import os
import re
import anthropic
import json
from prompts import teacher_prompt
from helpers import *

# Initialize Anthropic client
client = None

# Configuration Variables
MAX_TOKENS = 4096
TEMPERATURE = 1
SYSTEM_PROMPT = teacher_prompt

def conversation(history,selected_model):
  return client.messages.create(model=selected_model,
                              system=SYSTEM_PROMPT,
                              max_tokens=MAX_TOKENS,
                              temperature=TEMPERATURE,
                              stop_sequences=["</run_prompt>"],
                              messages=history)

# Again, from the Anthropic function calling book
def extract_between_tags(tag: str, string: str, strip: bool = False) -> list[str]:
    ext_list = re.findall(f"<{tag}>(.+?)</{tag}>", string, re.DOTALL)
    if strip:
        ext_list = [e.strip() for e in ext_list]
    return ext_list

def run_prompt(conversation_response, conversation_history, selected_model):
    conversation_response_text = conversation_response.content[0].text
    prompt_to_run = conversation_response_text.split("<run_prompt>")
    if len(prompt_to_run) > 1: prompt_to_run = prompt_to_run[1]
    else: prompt_to_run = prompt_to_run[0]

    # Get ready to extract data
    prompt_to_run = prompt_to_run.replace('\n',' ')
    prompt = extract_between_tags(tag="prompt",string=prompt_to_run)[0]
    test_vals = extract_between_tags(tag="test",string=prompt_to_run)[0]
    test_vals = json.loads(test_vals)
    test_vals = test_vals["test"]

    # Use the test cases to generate the test prompts
    prompts_to_eval=[]
    for test in test_vals:
        add_prompt = prompt
        for key, value in list(test.items()):
            add_prompt = add_prompt.replace(key,json.dumps(value))
        prompts_to_eval.append(add_prompt)

    # Evaluate the prompts and append the evaluation prompt and results
    evals = []
    for eval_prompt in prompts_to_eval:
        evaluation = client.messages.create(model=selected_model,
                                    max_tokens=MAX_TOKENS,
                                    temperature=TEMPERATURE,
                                    messages=[{"role":"user", "content":eval_prompt}])
        evaluation = evaluation.content[0].text
        evals.append((eval_prompt, evaluation))

    # Synthesize the AI response
    text_output = conversation_response.content[0].text
    text_output += '\n</run_prompt>'
    counter = 1
    for eval_prompt, result in evals:
        text_output += f'\n<test_{counter}>\n'
        text_output += eval_prompt
        text_output += f'\n</test_{counter}>'
        text_output += f'\n<result_{counter}>\n'
        text_output += result
        text_output += f'\n</result_{counter}>\n'
        counter += 1
    text_output += f'<scratchpad>\nI will now assess the results of the test cases.'

    complete_prompt_run = conversation_history.copy()
    complete_prompt_run.append({"role":"assistant", "content":text_output})

    # Finish the half-complete response, now with the prompt results
    test_response = client.messages.create(model=selected_model,
                                    max_tokens=MAX_TOKENS,
                                    temperature=TEMPERATURE,
                                    messages=complete_prompt_run)

    # Pass the fully completed message back
    conversation_response_text = text_output + '\n' + test_response.content[0].text

    return conversation_response_text

# Function to load session data from local storage
def load_data():
    if 'data' not in st.session_state:
        if os.path.exists('session_data.json'):
            with open('session_data.json', 'r') as file:
                data = json.load(file)
        else:
            data = {
                'conversations': {},
            }
        st.session_state['data'] = data
    return st.session_state['data']

# Function to save session data to local storage
def save_data(data):
    st.session_state['data'] = data
    with open('session_data.json', 'w') as file:
        json.dump(data, file, indent=2)

# Streamlit app
def main():
    global client

    st.title("Claude 3 Prompt Engineering Teacher")

    # Load session data from local storage
    data = load_data()
    conversations = data['conversations']

    # Show the "how-to" instructions in an expandable accordion
    st.expander("How to Use", expanded=False).markdown(how_to_text)

    name = st.sidebar.text_input("Please enter your name:")
    if name:
        st.session_state['name'] = name
    api_key_input = st.sidebar.text_input("Enter your Anthropic API key:", type="password")
    if api_key_input:
        client = anthropic.Anthropic(api_key=api_key_input)
        
    # Model selection
    model_options = ["claude-3-opus-20240229","claude-3-sonnet-20240229","claude-2.1","claude-2.0","claude-instant-1.2"]
    selected_model = st.sidebar.selectbox("Select Claude Model", model_options)

    # Sidebar
    st.sidebar.title("Conversation Sessions")
    session_name = st.sidebar.text_input("Enter session name")
    if st.sidebar.button("Create New Session"):
        if session_name not in conversations:
            conversations[session_name] = []
            data['conversations'] = conversations
            save_data(data)
            st.session_state.selected_session = session_name
            st.rerun()

    # Session selection and deletion
    session_list = list(conversations.keys())
    if session_list:
        selected_session = st.sidebar.selectbox("Select Session", session_list)
        if st.sidebar.button("Load Session"):
            st.session_state.selected_session = selected_session
            st.rerun()
        if st.sidebar.button("Delete Session"):
            del conversations[selected_session]
            data['conversations'] = conversations
            save_data(data)
            st.session_state.pop('selected_session', None)
            st.rerun()
    else:
        selected_session = None

    # Import/Export session data
    if st.sidebar.button("Export Session Data"):
        session_data = json.dumps(data['conversations'], indent=2)
        st.sidebar.download_button(
            label="Download Session Data",
            data=session_data,
            file_name="session_data.json",
            mime="application/json"
        )

    uploaded_file = st.sidebar.file_uploader("Import Session Data", type=["json"])
    if uploaded_file is not None:
        session_data = json.load(uploaded_file)
        data['conversations'].update(session_data)
        save_data(data)
        st.sidebar.success("Session data imported successfully.")
        st.sidebar.info("Please select a session or create a new one.")
        return

    # Current session indicator
    if 'selected_session' in st.session_state:
        st.write(f"Current Session: **{st.session_state.selected_session}**")
    else:
        st.write("No session selected.")

    # Conversation display and user input
    if 'selected_session' in st.session_state:
        selected_session = st.session_state.selected_session
        if name is not None and api_key_input is not None:
            conversation_history = data['conversations'][selected_session]
            for message in conversation_history:
                if message['role'] == 'user':
                    st.markdown(f"**User:** {message['content']}")
                else:
                    st.markdown(f"**Assistant:** {message['content']}")

            if len(conversation_history)==0:
                if st.button("Start"):
                    conversation_history.append({'role': 'user', 'content': name})
                    ai_response = conversation(conversation_history,selected_model)
                    ai_response = ai_response.content[0].text
                    conversation_history.append({'role': 'assistant', 'content': ai_response})
                    data['conversations'][selected_session] = conversation_history
                    save_data(data)
                    st.rerun()
            else:
                user_input = st.text_input("Enter your message")
                if st.button("Send"):
                    conversation_history.append({'role': 'user', 'content': user_input})
                    ai_response = conversation(conversation_history,selected_model)
                    if ai_response.stop_sequence == "</run_prompt>":
                        ai_response = run_prompt(ai_response, conversation_history,selected_model)
                    else:
                        ai_response = ai_response.content[0].text
                    conversation_history.append({'role': 'assistant', 'content': ai_response})
                    data['conversations'][selected_session] = conversation_history
                    save_data(data)
                    st.rerun()
        else:
            st.info("Please add your name and API key.")
    else:
        st.info("No conversation session selected. Please create a new session or select an existing one.")

if __name__ == '__main__':
    main()