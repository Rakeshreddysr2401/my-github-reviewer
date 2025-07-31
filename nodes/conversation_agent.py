# nodes/conversation_agent.py
from States.state import ReviewState
import openai
import os

def conversation_agent(state: ReviewState) -> ReviewState:
    print(f"state before conversation agent {state}")
    """
    Calls the OpenAI API with the conversation prompt to generate a reply.
    """
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    # prompt = state.context_prompt
    #
    # # Basic OpenAI Chat API call
    # response = openai.ChatCompletion.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful code reviewer bot."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.5
    # )
    #
    # # Extract reply text
    # reply = response["choices"][0]["message"]["content"].strip()
    # state.generated_reply = reply
    return state
