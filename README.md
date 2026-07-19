# My First LangChain Agent 🦜🔗

A tiny, beginner-friendly **AI agent** built with [LangChain](https://docs.langchain.com/) and Python — running **entirely in Docker**. It uses a **local** LLM through [Ollama](https://ollama.com), so there's **no API key and no cost**.

The agent can chat, and it can call two custom Python **tools**:
- 🧮 `calculator` — does arithmetic
- 🕒 `current_time` — tells the current date & time

---

## What are these words?

- **LLM** — the language model that generates text (here, `llama3.2` running locally via Ollama).
- **Tool** — a plain Python function the model is allowed to call when it needs to (e.g. real math instead of guessing).
- **Agent** — the loop that lets the model *decide* whether to answer directly or call a tool first, then respond.

---

## Prerequisites

The **only** thing you need installed is **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**. No Python, no Ollama, nothing else.

> First run downloads the Ollama image and the `llama3.2` model (~2 GB), so it takes a few minutes. After that it's cached.

---

## Configuration

All settings live in a **`.env`** file (model, Ollama URL/port, timezone). A `.env` is included; to customize, copy the template and edit:
```bash
cp .env.example .env
```

| Variable | Default | Meaning |
|----------|---------|---------|
| `OLLAMA_MODEL` | `llama3.2` | model the agent uses (must be pulled) |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | where the app reaches Ollama |
| `OLLAMA_PORT` | `11434` | host port for the Ollama container |
| `TZ` | `Asia/Riyadh` | timezone for the `current_time` tool |

## Run it — step by step

**1. Start the Ollama model server** (in the background):
```bash
docker compose up -d ollama
```

**2. Pull the model into the Ollama container** (one time — it's cached afterward):
```bash
docker compose exec ollama ollama pull llama3.2
```

**3. Build and start the agent** (interactive chat):
```bash
docker compose run --rm app
```

You'll see a prompt. Try:
```
you > what is 128 * 4?          # -> uses the calculator tool
you > what time is it?          # -> uses the current_time tool
you > who wrote Hamlet?         # -> answered directly, no tool
```

Type `exit` to quit.

> **Timezone:** the container defaults to **`Asia/Riyadh`**. Override with the
> `TZ` variable if needed:
> ```bash
> TZ=Europe/London docker compose run --rm app
> ```

**4. Stop everything** when done:
```bash
docker compose down
```
The downloaded model stays in the `ollama_data` volume, so next time you can skip step 2.

---

## How it works

Two containers, defined in [`docker-compose.yml`](docker-compose.yml):

| Service  | What it is | Role |
|----------|------------|------|
| `ollama` | official `ollama/ollama` image | serves the local LLM on port `11434`, caches models in a volume |
| `app`    | built from our [`Dockerfile`](Dockerfile) | runs [`main.py`](main.py), talks to `ollama` at `http://ollama:11434` |

The agent code in [`main.py`](main.py) follows four numbered steps:

1. **Define tools** with the `@tool` decorator — the docstring tells the model *when* to use each one.
2. **Create the model** with `ChatOllama(...)`, pointed at the Ollama container.
3. **Create the agent** with `create_agent(model=llm, tools=[...])`.
4. **Chat loop** — read your input, `agent.invoke(...)`, print the reply.

---

## Next step (optional)

Give the agent **memory** so it remembers earlier messages in the conversation, using LangChain's `InMemorySaver` checkpointer and a `thread_id`. A natural follow-up once this works.

## Sources
- [LangChain Agents docs](https://docs.langchain.com/oss/python/langchain/agents)
- [Ollama Docker image](https://hub.docker.com/r/ollama/ollama)
