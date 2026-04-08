"""
llm_interface.py
Model-agnostic LLM adapter layer.

Swap providers with a single string:
    llm = get_llm("openai")
    llm = get_llm("claude")
    llm = get_llm("gemini")
    llm = get_llm("ollama", model="llama3")
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Shared response dataclass — provider-neutral
# ---------------------------------------------------------------------------

@dataclass
class TokenUsage:
    """Token usage statistics from a single LLM call."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class Message:
    role: str                        # "assistant" | "tool"
    content: str = ""
    tool_calls: list[dict] = field(default_factory=list)   # [{name, args}]
    usage: TokenUsage | None = None


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class LLMBase(ABC):
    """All providers must implement this single method."""

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> Message:
        """Send messages and return a normalised Message."""


# ---------------------------------------------------------------------------
# OpenAI  (pip install openai)
# ---------------------------------------------------------------------------

class OpenAIAdapter(LLMBase):
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.7):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("pip install openai")
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature

    def chat(self, messages, tools=None) -> Message:
        kwargs: dict[str, Any] = dict(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        if tools:
            kwargs["tools"] = [
                {"type": "function", "function": t} for t in tools
            ]
            kwargs["tool_choice"] = "auto"

        resp = self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0].message

        tool_calls = []
        if choice.tool_calls:
            for tc in choice.tool_calls:
                import json
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "args": json.loads(tc.function.arguments),
                })

        # Extract token usage
        usage = None
        if hasattr(resp, 'usage') and resp.usage:
            usage = TokenUsage(
                prompt_tokens=resp.usage.prompt_tokens or 0,
                completion_tokens=resp.usage.completion_tokens or 0,
                total_tokens=resp.usage.total_tokens or 0,
            )

        return Message(
            role="assistant",
            content=choice.content or "",
            tool_calls=tool_calls,
            usage=usage,
        )


# ---------------------------------------------------------------------------
# Anthropic / Claude  (pip install anthropic)
# ---------------------------------------------------------------------------

class ClaudeAdapter(LLMBase):
    def __init__(self, model: str = "claude-opus-4-5", temperature: float = 0.7):
        try:
            import anthropic
        except ImportError:
            raise ImportError("pip install anthropic")
        self.client = anthropic.Anthropic()
        self.model = model
        self.temperature = temperature

    def chat(self, messages, tools=None) -> Message:
        import anthropic

        # Claude keeps system separate
        system = ""
        filtered = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                filtered.append(m)

        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=4096,
            messages=filtered,
            temperature=self.temperature,
        )
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = [
                {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "input_schema": t.get("parameters", {"type": "object", "properties": {}}),
                }
                for t in tools
            ]

        resp = self.client.messages.create(**kwargs)

        tool_calls = []
        text = ""
        for block in resp.content:
            if block.type == "text":
                text += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "args": block.input,
                })

        # Extract token usage
        usage = None
        if hasattr(resp, 'usage') and resp.usage:
            usage = TokenUsage(
                prompt_tokens=getattr(resp.usage, 'input_tokens', 0),
                completion_tokens=getattr(resp.usage, 'output_tokens', 0),
                total_tokens=(getattr(resp.usage, 'input_tokens', 0)
                              + getattr(resp.usage, 'output_tokens', 0)),
            )

        return Message(role="assistant", content=text, tool_calls=tool_calls, usage=usage)


# ---------------------------------------------------------------------------
# Google Gemini  (pip install google-generativeai)
# ---------------------------------------------------------------------------

class GeminiAdapter(LLMBase):
    def __init__(self, model: str = "gemini-1.5-pro", temperature: float = 0.7):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("pip install google-generativeai")
        import os
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.genai = genai
        self.model_name = model
        self.temperature = temperature

    def chat(self, messages, tools=None) -> Message:
        import json

        # Convert messages to Gemini format
        history = []
        system_instruction = None
        for m in messages:
            if m["role"] == "system":
                system_instruction = m["content"]
            elif m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})

        generation_config = self.genai.types.GenerationConfig(
            temperature=self.temperature
        )
        model = self.genai.GenerativeModel(
            self.model_name,
            system_instruction=system_instruction,
            generation_config=generation_config,
        )
        chat = model.start_chat(history=history[:-1] if history else [])
        last_user = history[-1]["parts"][0] if history else ""

        resp = chat.send_message(last_user)

        # Extract token usage from Gemini
        usage = None
        if hasattr(resp, 'usage_metadata') and resp.usage_metadata:
            um = resp.usage_metadata
            usage = TokenUsage(
                prompt_tokens=getattr(um, 'prompt_token_count', 0),
                completion_tokens=getattr(um, 'candidates_token_count', 0),
                total_tokens=getattr(um, 'total_token_count', 0),
            )

        return Message(role="assistant", content=resp.text, tool_calls=[], usage=usage)


# ---------------------------------------------------------------------------
# Ollama  (pip install ollama  +  ollama server running locally or remotely)
# ---------------------------------------------------------------------------

class OllamaAdapter(LLMBase):
    def __init__(
        self,
        model: str = "qwen3.5:35b",
        temperature: float = 0.2,
        base_url: str | None = None,
    ):
        try:
            import ollama as _ollama
        except ImportError:
            raise ImportError("pip install ollama")
        self._ollama = _ollama
        if base_url:
            self.client = _ollama.Client(host=base_url)
        else:
            self.client = _ollama.Client()
        self.model = model
        self.temperature = temperature

    def chat(self, messages, tools=None) -> Message:
        import json as _json

        kwargs: dict[str, Any] = dict(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature},
        )
        # Pass tools in OpenAI-compatible format if provided
        if tools:
            kwargs["tools"] = [
                {"type": "function", "function": t} for t in tools
            ]

        resp = self.client.chat(**kwargs)

        # Parse response — Ollama returns a ChatResponse object or dict
        msg = resp.get("message", resp) if isinstance(resp, dict) else resp.message
        content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "") or ""

        # Parse tool calls — Ollama returns them in msg["tool_calls"] or msg.tool_calls
        raw_tool_calls = (
            msg.get("tool_calls", []) if isinstance(msg, dict)
            else getattr(msg, "tool_calls", None) or []
        )
        tool_calls = []
        for tc in raw_tool_calls:
            # Ollama tool_call format: {"function": {"name": ..., "arguments": {...}}}
            if isinstance(tc, dict):
                fn = tc.get("function", tc)
                name = fn.get("name", "")
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = _json.loads(args)
                    except _json.JSONDecodeError:
                        args = {"raw": args}
            else:
                # Object-style (ollama SDK response objects)
                fn = getattr(tc, "function", tc)
                name = getattr(fn, "name", "")
                args = getattr(fn, "arguments", {})
                if isinstance(args, str):
                    try:
                        args = _json.loads(args)
                    except _json.JSONDecodeError:
                        args = {"raw": args}
            tool_calls.append({
                "id": f"ollama_{name}_{len(tool_calls)}",
                "name": name,
                "args": args,
            })

        # Extract token usage
        usage = None
        if isinstance(resp, dict):
            prompt_tokens = resp.get('prompt_eval_count', 0) or 0
            completion_tokens = resp.get('eval_count', 0) or 0
        else:
            prompt_tokens = getattr(resp, 'prompt_eval_count', 0) or 0
            completion_tokens = getattr(resp, 'eval_count', 0) or 0
        if prompt_tokens or completion_tokens:
            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            )

        return Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
            usage=usage,
        )



# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

PROVIDERS = {
    "openai": OpenAIAdapter,
    "claude": ClaudeAdapter,
    "gemini": GeminiAdapter,
    "ollama": OllamaAdapter,
}


def get_llm(
    provider: str = "openai",
    model: str | None = None,
    temperature: float = 0.7,
    base_url: str | None = None,
) -> LLMBase:
    """
    Return a model-agnostic LLM adapter.

    Args:
        provider:    "openai" | "claude" | "gemini" | "ollama"
        model:       Optional model override (uses provider default if None)
        temperature: Sampling temperature (0.0–1.0, default 0.7)
        base_url:    Optional base URL for remote instances (Ollama only)

    Examples:
        llm = get_llm("openai")
        llm = get_llm("claude", model="claude-sonnet-4-5")
        llm = get_llm("ollama", model="qwen3.5:35b")
        llm = get_llm("ollama", model="qwen3.5:35b", base_url="http://remote:11434")
    """
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider '{provider}'. Choose from: {list(PROVIDERS)}")
    cls = PROVIDERS[provider]
    kwargs: dict[str, Any] = {"temperature": temperature}
    if model:
        kwargs["model"] = model
    if base_url and provider == "ollama":
        kwargs["base_url"] = base_url
    return cls(**kwargs)

