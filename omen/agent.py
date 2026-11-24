import json
import requests
from openai import OpenAI
from omen.config import (
    OLLAMA_BASE_URL, OLLAMA_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL,
    CLOUD_MODEL, PROVIDER_MODE, MAX_TOOL_ROUNDS
)
from omen.tools import (
    tool_definitions, calculate, current_time, list_workspace_files, read_workspace_file
)

SYSTEM_PROMPT = """You are OMEN, a helpful, capable personal AI agent.
Understand the user's goal, plan briefly when useful, select tools when they help,
and explain the outcome. Reply in the language the user uses, including English,
Hindi or Marathi when supported by the model.
Never claim a tool succeeded unless its result confirms it. Save notes only when
the user explicitly asks you to remember or save something.
You may read text files only from the workspace folder. Never claim unrestricted PC access.
Do not invent tool results. Ask one clear question when essential information is missing.
"""

class OmenAgent:
    def __init__(self, memory):
        self.memory = memory
        self.cloud = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL) if OPENAI_API_KEY else None

    def _execute(self, name, args):
        funcs = {
            "calculate": lambda: calculate(args["expression"]),
            "current_time": current_time,
            "save_memory": lambda: self.memory.save_note(args["content"]),
            "search_memory": lambda: json.dumps(self.memory.search_notes(args["query"]), ensure_ascii=False),
            "list_workspace_files": list_workspace_files,
            "read_workspace_file": lambda: read_workspace_file(args["filename"]),
        }
        if name not in funcs:
            raise ValueError(f"Tool not permitted: {name}")
        return funcs[name]()

    def _local_chat(self, messages):
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": messages,
                  "tools": tool_definitions(), "stream": False},
            timeout=180
        )
        response.raise_for_status()
        return response.json()["message"]

    def _cloud_chat(self, messages):
        if not self.cloud:
            raise RuntimeError("Cloud provider selected but OPENAI_API_KEY is not configured.")
        response = self.cloud.chat.completions.create(
            model=CLOUD_MODEL,
            messages=messages,
            tools=tool_definitions(),
            tool_choice="auto"
        )
        msg = response.choices[0].message
        return {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {"id": call.id, "type": "function",
                 "function": {"name": call.function.name, "arguments": call.function.arguments}}
                for call in (msg.tool_calls or [])
            ]
        }

    def _provider_order(self):
        if PROVIDER_MODE == "local":
            return ["local"]
        if PROVIDER_MODE == "cloud":
            return ["cloud"]
        # Privacy-first hybrid: use local first, fall back to cloud if local is unavailable.
        return ["local", "cloud"] if self.cloud else ["local"]

    def _ask(self, messages):
        errors = []
        for provider in self._provider_order():
            try:
                msg = self._local_chat(messages) if provider == "local" else self._cloud_chat(messages)
                return msg, provider
            except Exception as exc:
                errors.append(f"{provider}: {exc}")
        raise RuntimeError("No configured AI provider responded. " + " | ".join(errors))

    def run(self, conversation):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Keep a bounded context window; preserve the latest user/assistant turns.
        messages.extend(conversation[-16:])
        trace, provider_used = [], "unknown"

        for round_no in range(MAX_TOOL_ROUNDS + 1):
            msg, provider_used = self._ask(messages)
            messages.append(msg)
            calls = msg.get("tool_calls") or []
            if not calls:
                return msg.get("content") or "I couldn't produce a response.", trace, provider_used

            if round_no >= MAX_TOOL_ROUNDS:
                return "I reached the tool-use limit. Please split this into smaller tasks.", trace, provider_used

            for call in calls:
                fn = call.get("function", {})
                name = fn.get("name", "")
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    args = json.loads(args)
                try:
                    result = self._execute(name, args)
                    trace.append(f"{name}: completed")
                except Exception as exc:
                    result = f"Tool error: {exc}"
                    trace.append(f"{name}: {exc}")
                tool_message = {"role": "tool", "content": str(result)}
                if call.get("id"):
                    tool_message["tool_call_id"] = call["id"]
                messages.append(tool_message)
        return "I couldn't finish within the tool-use limit.", trace, provider_used
