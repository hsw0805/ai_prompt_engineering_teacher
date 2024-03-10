import streamlit as st

how_to_text = """
This app is designed to help you learn and improve your prompt engineering skills through a series of roles and interactions. Here's how it works:

1. Start by entering your Anthropic API key, your name, and creating a new session. The app will greet you and provide an introductory message explaining the different roles and their goals.

2. The app will begin in the Skill-gauging Role, where it will present you with a prompt engineering question in the form of a task to be done. Your goal is to provide a prompt that can be run in Claude to handle this task.

   - When writing your prompt, identify variables within the prompt using variable names in all caps surrounded by double curly braces, such as {{INPUT_VARIABLE}}.
   - After submitting your prompt, the app will generate test cases and run them against your prompt to assess its effectiveness.

3. Based on your performance in the Skill-gauging Role, the app will switch to the Curriculum Planner role. It will create a personalized curriculum to help you improve your prompt engineering skills, addressing your weaknesses and building additional skills. You'll have the opportunity to review and provide input on the curriculum plan.

4. Once the curriculum plan is approved, the app will move to the Material Generator role. It will create a set of potential tasks that can be solved with Claude prompts and develop a project-based learning plan using these tasks. You'll have the chance to review and provide feedback on the learning plan.

5. After approving the project-based learning plan, the app will transition to the Teacher role. It will guide you through the projects, providing explanations, strategies, and tips to help you learn and improve your prompt engineering skills.

   - As you work on each project, you'll submit your prompts to the app for evaluation. The app will generate test cases, run them against your prompt, and provide feedback on how to improve your solution.
   - Remember to use double curly braces, such as {{INPUT_VARIABLE}}, as placeholders for variables in your prompts.
   - You'll iterate and refine your prompts based on the app's feedback until you've mastered the skills targeted by the project.

6. Once you've successfully completed a project, the app will move you to the next project in the learning plan, continuing in the Teacher role until you've finished all the projects and achieved the goal of becoming a skilled prompt engineer.

Throughout the process, feel free to ask clarifying questions whenever needed. The app is here to support your learning journey and help you become a proficient prompt engineer.

You can collapse this "How to Use This App" guide by clicking on the title at the top.
"""