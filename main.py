"""
My First LangChain Agent
========================

A minimal agent that runs a local LLM (via Ollama) and can call custom Python
tools. Read top to bottom — each step is numbered and commented.

Flow of one turn:
    you type a question
        -> the agent sends it to the model
        -> the model decides whether it needs a tool
        -> if so, LangChain runs the tool and feeds the result back
        -> the model writes the final answer
"""

import os
from datetime import datetime

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


# ---------------------------------------------------------------------------
# STEP 1: Define tools.
# A "tool" is just a Python function the agent is allowed to call. The @tool
# decorator turns it into something the model can invoke, and the docstring is
# what the model reads to decide WHEN to use it — so keep docstrings clear.
# ---------------------------------------------------------------------------
@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '2 + 2 * 3' or '128 * 4'.

    Use this for any math question instead of trying to compute it yourself.
    """
    # Only allow characters that appear in simple arithmetic — this keeps the
    # eval() safe from running arbitrary code.
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Error: only numbers and + - * / ( ) are allowed."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
    except Exception as exc:  # noqa: BLE001 - report any math error to the model
        return f"Error: could not evaluate '{expression}' ({exc})."
    return str(result)


@tool
def current_time() -> str:
    """Return the current date and time. Use this for 'what time is it'.

    Uses the timezone from the TZ environment variable (see docker-compose.yml);
    the reply includes the timezone name so it is unambiguous.
    """
    now = datetime.now().astimezone()
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


# ---------------------------------------------------------------------------
# STEP 2: Create the model.
# ChatOllama talks to the Ollama server. In Docker, base_url points at the
# 'ollama' service; OLLAMA_BASE_URL is set for us in docker-compose.yml.
# ---------------------------------------------------------------------------
llm = ChatOllama(
    model=os.environ.get("OLLAMA_MODEL", "llama3.2"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434"),
    temperature=0,  # deterministic answers, good for a tutorial
)

# ---------------------------------------------------------------------------
# STEP 3: Create the agent.
# create_agent wires the model together with the tools. The returned agent
# handles the whole "think -> maybe call a tool -> answer" loop for us.
# ---------------------------------------------------------------------------
agent = create_agent(model=llm, tools=[calculator, current_time])


# ---------------------------------------------------------------------------
# STEP 4: Run it — a simple interactive chat loop.
# ---------------------------------------------------------------------------
def main() -> None:
    print("My First LangChain Agent (type 'exit' to quit)")
    print("Try: 'what is 128 * 4?'  |  'what time is it?'  |  'who wrote Hamlet?'\n")

    while True:
        try:
            user_input = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("bye!")
            break

        # Send the message to the agent and print its final reply.
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )
        answer = result["messages"][-1].content
        print(f"agent > {answer}\n")


if __name__ == "__main__":
    main()
