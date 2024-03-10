import streamlit as st

how_to_text = """
This app is designed to help you learn and improve your prompt engineering skills. Here's how to use it:

1. Start by entering your Anthropic API key and your name in the left panel.

   - Security note: This app does not store your API key. Your API key is only used to run the LLM.

2. If you have no existing sessions, create a new session in the left panel. Don't forget to name your session!

3. If you have any pre-existing sessions, you can also load a session.

4. When submitting a prompt to Claude, identify variables within the prompt using variable names in all caps surrounded by double curly braces, such as {{INPUT_VARIABLE}}.

5. Throughout the process, feel free to ask clarifying questions whenever needed.

You can collapse this "How to Use This App" guide by clicking on the title at the top.
"""