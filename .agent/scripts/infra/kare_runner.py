"""
KARE Runner — Runtime Portability Layer (Fase 3 / F3.1)
========================================================
Interface abstrata BaseRunner + adapters para executar agentes KARE
fora do VS Code, contra qualquer LLM OpenAI-compatible.

Arquitetura:
  BaseRunner (ABC) — interface agnóstica de modelo
    ├── CopilotRunner  — stub; runtime primário é o VS Code
    ├── OpenAIRunner   — OpenAI API ou endpoint OpenAI-compatible (Groq, Together, Azure)
    ├── AnthropicRunner — Anthropic API (Claude)
    └── OllamaRunner   — Ollama local (sem autenticação)

Uso:
    # Listar agentes disponíveis
    python kare_runner.py list

    # Executar agente via OpenAI-compatible API
    python kare_runner.py run --agent story-crafter \\
        --prompt "Crie story para login OAuth" \\
        --adapter openai --api-key $OPENAI_API_KEY --model gpt-4o

    # Executar via Anthropic
    python kare_runner.py run --agent product-discovery \\
        --prompt "Novo produto de cobrança automática" \\
        --adapter anthropic --api-key $ANTHROPIC_API_KEY \\
        --model claude-3-5-sonnet-20241022

    # Executar via Ollama local
    python kare_runner.py run --agent project-classifier \\
        --prompt "Classifique este repositório Python/Django" \\
        --adapter ollama --model llama3.1

    # Verificar estado de todos os adapters
    python kare_runner.py health
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Paths ─────────────────────────────────────────────────────────────────────

WORKSPACE = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = WORKSPACE / ".agent" / "agents"
SKILLS_DIR = WORKSPACE / ".agent" / "skills"


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class AgentManifest:
    name: str
    description: str
    skills: list[str] = field(default_factory=list)
    max_retries: int = 3
    system_prompt: str = ""
    raw_md: str = ""


@dataclass
class RunResult:
    agent: str
    adapter: str
    model: str
    prompt: str
    response: str
    latency_ms: int
    tokens_est: int
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


# ── Agent loader ──────────────────────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            # handle list values (skills: [...] or yaml list)
            if v.startswith("["):
                out[k] = [i.strip().strip("'\"") for i in v.strip("[]").split(",") if i.strip()]
            else:
                out[k] = v
    return out


def _extract_body(text: str) -> str:
    m = _FRONTMATTER_RE.match(text)
    if m:
        return text[m.end():]
    return text


def load_agent(name: str) -> AgentManifest:
    """Load an agent .md file and return its manifest."""
    path = AGENTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Agent not found: {path}")
    raw = path.read_text(encoding="utf-8")
    fm = _parse_frontmatter(raw)
    body = _extract_body(raw)

    skills = fm.get("skills", [])
    if isinstance(skills, str):
        skills = [skills]

    # Build system prompt from skills + body
    skill_blocks: list[str] = []
    for s in skills:
        skill_md = SKILLS_DIR / s / "SKILL.md"
        if skill_md.exists():
            skill_blocks.append(skill_md.read_text(encoding="utf-8"))

    system_prompt = "\n\n---\n\n".join(skill_blocks) + "\n\n---\n\n" + body if skill_blocks else body

    return AgentManifest(
        name=name,
        description=fm.get("description", ""),
        skills=skills,
        max_retries=int(fm.get("max_retries", 3)),
        system_prompt=system_prompt,
        raw_md=raw,
    )


def list_agents() -> list[str]:
    return sorted(p.stem for p in AGENTS_DIR.glob("*.md"))


# ── Abstract runner ───────────────────────────────────────────────────────────

class BaseRunner(ABC):
    """Runtime-agnostic interface for invoking KARE agents."""

    adapter_name: str = "base"

    @abstractmethod
    def invoke(self, agent: AgentManifest, prompt: str, **kwargs: Any) -> RunResult:
        """Execute the agent with the given user prompt."""

    @abstractmethod
    def health(self) -> dict:
        """Return health status: {ok: bool, message: str}"""

    def invoke_with_retry(self, agent: AgentManifest, prompt: str, **kwargs: Any) -> RunResult:
        last: RunResult | None = None
        for attempt in range(1, agent.max_retries + 1):
            result = self.invoke(agent, prompt, **kwargs)
            if result.success:
                return result
            last = result
            print(f"[RETRY {attempt}/{agent.max_retries}] {result.error}", file=sys.stderr)
        return last  # type: ignore[return-value]


# ── OpenAI / OpenAI-compatible adapter ───────────────────────────────────────

class OpenAIRunner(BaseRunner):
    """Adapter for OpenAI API and any OpenAI-compatible endpoint (Groq, Together, Azure)."""

    adapter_name = "openai"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o",
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.model = model

    def invoke(self, agent: AgentManifest, prompt: str, **kwargs: Any) -> RunResult:
        import urllib.request
        import urllib.error

        if not self.api_key:
            return RunResult(agent.name, self.adapter_name, self.model, prompt, "",
                             0, 0, error="OPENAI_API_KEY not set")

        payload = json.dumps({
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "system", "content": agent.system_prompt},
                {"role": "user",   "content": prompt},
            ],
            "max_tokens": kwargs.get("max_tokens", 4096),
        }).encode()

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read())
            latency = int((time.monotonic() - t0) * 1000)
            text = body["choices"][0]["message"]["content"]
            usage = body.get("usage", {})
            tokens = usage.get("total_tokens", len(text) // 4)
            return RunResult(agent.name, self.adapter_name, self.model, prompt,
                             text, latency, tokens)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            return RunResult(agent.name, self.adapter_name, self.model, prompt, "",
                             0, 0, error=f"HTTP {e.code}: {detail[:200]}")
        except Exception as e:
            return RunResult(agent.name, self.adapter_name, self.model, prompt, "",
                             0, 0, error=str(e))

    def health(self) -> dict:
        if not self.api_key:
            return {"ok": False, "message": "OPENAI_API_KEY not set"}
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            with urllib.request.urlopen(req, timeout=10):
                pass
            return {"ok": True, "message": f"Connected to {self.base_url}"}
        except Exception as e:
            return {"ok": False, "message": str(e)}


# ── Anthropic adapter ─────────────────────────────────────────────────────────

class AnthropicRunner(BaseRunner):
    """Adapter for Anthropic Messages API (Claude models)."""

    adapter_name = "anthropic"
    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-3-5-sonnet-20241022",
    ) -> None:
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = model

    def invoke(self, agent: AgentManifest, prompt: str, **kwargs: Any) -> RunResult:
        import urllib.request
        import urllib.error

        if not self.api_key:
            return RunResult(agent.name, self.adapter_name, self.model, prompt, "",
                             0, 0, error="ANTHROPIC_API_KEY not set")

        payload = json.dumps({
            "model": kwargs.get("model", self.model),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "system": agent.system_prompt,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()

        req = urllib.request.Request(
            self.API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": self.API_VERSION,
            },
            method="POST",
        )
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read())
            latency = int((time.monotonic() - t0) * 1000)
            text = body["content"][0]["text"]
            usage = body.get("usage", {})
            tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            return RunResult(agent.name, self.adapter_name, self.model, prompt,
                             text, latency, tokens)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            return RunResult(agent.name, self.adapter_name, self.model, prompt, "",
                             0, 0, error=f"HTTP {e.code}: {detail[:200]}")
        except Exception as e:
            return RunResult(agent.name, self.adapter_name, self.model, prompt, "",
                             0, 0, error=str(e))

    def health(self) -> dict:
        if not self.api_key:
            return {"ok": False, "message": "ANTHROPIC_API_KEY not set"}
        # Anthropic has no dedicated /health endpoint; try a minimal message
        try:
            result = self.invoke(
                AgentManifest("health-check", "", system_prompt="You are a health check."),
                "Reply with: OK",
                max_tokens=5,
            )
            if result.success:
                return {"ok": True, "message": f"Anthropic API reachable ({self.model})"}
            return {"ok": False, "message": result.error}
        except Exception as e:
            return {"ok": False, "message": str(e)}


# ── Ollama adapter ────────────────────────────────────────────────────────────

class OllamaRunner(BaseRunner):
    """Adapter for Ollama local inference server."""

    adapter_name = "ollama"

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.1",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def invoke(self, agent: AgentManifest, prompt: str, **kwargs: Any) -> RunResult:
        import urllib.request
        import urllib.error

        payload = json.dumps({
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "system", "content": agent.system_prompt},
                {"role": "user",   "content": prompt},
            ],
            "stream": False,
        }).encode()

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                body = json.loads(resp.read())
            latency = int((time.monotonic() - t0) * 1000)
            text = body["message"]["content"]
            tokens = body.get("prompt_eval_count", 0) + body.get("eval_count", 0)
            return RunResult(agent.name, self.adapter_name, self.model, prompt,
                             text, latency, tokens)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            return RunResult(agent.name, self.adapter_name, self.model, prompt, "",
                             0, 0, error=f"HTTP {e.code}: {detail[:200]}")
        except Exception as e:
            return RunResult(agent.name, self.adapter_name, self.model, prompt, "",
                             0, 0, error=str(e))

    def health(self) -> dict:
        try:
            import urllib.request
            with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=5) as resp:
                body = json.loads(resp.read())
            models = [m["name"] for m in body.get("models", [])]
            return {"ok": True, "message": f"Ollama running. Models: {', '.join(models) or 'none'}"}
        except Exception as e:
            return {"ok": False, "message": str(e)}


# ── CopilotRunner stub ────────────────────────────────────────────────────────

class CopilotRunner(BaseRunner):
    """
    Stub — runtime primário é o VS Code / GitHub Copilot Chat.
    Não implementável via Python puro; documentado aqui para completar a interface.
    """

    adapter_name = "copilot"

    def invoke(self, agent: AgentManifest, prompt: str, **kwargs: Any) -> RunResult:
        return RunResult(agent.name, self.adapter_name, "github-copilot", prompt, "",
                         0, 0, error="CopilotRunner não é executável fora do VS Code. Use OpenAIRunner, AnthropicRunner ou OllamaRunner.")

    def health(self) -> dict:
        return {"ok": False, "message": "CopilotRunner requer VS Code. Verifique a extensão GitHub Copilot Chat."}


# ── Factory ───────────────────────────────────────────────────────────────────

ADAPTERS: dict[str, type[BaseRunner]] = {
    "openai":    OpenAIRunner,
    "anthropic": AnthropicRunner,
    "ollama":    OllamaRunner,
    "copilot":   CopilotRunner,
}


def build_runner(
    adapter: str,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> BaseRunner:
    cls = ADAPTERS.get(adapter)
    if cls is None:
        raise ValueError(f"Unknown adapter '{adapter}'. Available: {list(ADAPTERS)}")
    kwargs: dict[str, Any] = {}
    if api_key:
        kwargs["api_key"] = api_key
    if model:
        kwargs["model"] = model
    if base_url and adapter == "openai":
        kwargs["base_url"] = base_url
    if base_url and adapter == "ollama":
        kwargs["base_url"] = base_url
    return cls(**kwargs)  # type: ignore[arg-type]


# ── CLI ───────────────────────────────────────────────────────────────────────

def cmd_list(_args: argparse.Namespace) -> None:
    agents = list_agents()
    print(f"{'Agent':<30} {'Description'}")
    print("-" * 70)
    for name in agents:
        try:
            m = load_agent(name)
            desc = m.description[:40].replace("\n", " ")
        except Exception:
            desc = "(erro ao carregar)"
        print(f"{name:<30} {desc}")
    print(f"\nTotal: {len(agents)} agentes em {AGENTS_DIR}")


def cmd_run(args: argparse.Namespace) -> None:
    try:
        agent = load_agent(args.agent)
    except FileNotFoundError as e:
        print(f"[ERRO] {e}", file=sys.stderr)
        sys.exit(1)

    runner = build_runner(
        args.adapter,
        api_key=args.api_key,
        model=args.model,
        base_url=args.base_url,
    )

    print(f"[KARE Runner] Invocando @{agent.name} via {args.adapter}...", file=sys.stderr)
    result = runner.invoke_with_retry(agent, args.prompt)

    if not result.success:
        print(f"[ERRO] {result.error}", file=sys.stderr)
        sys.exit(1)

    print(result.response)
    print(f"\n[latency: {result.latency_ms}ms | tokens: {result.tokens_est}]", file=sys.stderr)

    if args.output:
        Path(args.output).write_text(result.response, encoding="utf-8")
        print(f"[Salvo em {args.output}]", file=sys.stderr)


def cmd_health(_args: argparse.Namespace) -> None:
    print("KARE Runner — Health Check\n")
    for name, cls in ADAPTERS.items():
        try:
            runner = cls()
            status = runner.health()
        except Exception as e:
            status = {"ok": False, "message": str(e)}
        icon = "✅" if status["ok"] else "❌"
        print(f"  {icon} {name:<12} {status['message']}")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kare_runner",
        description="KARE Runtime Portability Layer — execute agents outside VS Code",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # list
    sub.add_parser("list", help="List available agents")

    # run
    run_p = sub.add_parser("run", help="Invoke an agent")
    run_p.add_argument("--agent",   required=True, help="Agent name (e.g. story-crafter)")
    run_p.add_argument("--prompt",  required=True, help="User prompt")
    run_p.add_argument("--adapter", default="openai",
                       choices=list(ADAPTERS), help="LLM adapter")
    run_p.add_argument("--api-key", dest="api_key", default=None)
    run_p.add_argument("--model",   default=None)
    run_p.add_argument("--base-url", dest="base_url", default=None,
                       help="Override API base URL (OpenAI-compatible endpoints)")
    run_p.add_argument("--output",  default=None, help="Save response to file")

    # health
    sub.add_parser("health", help="Check adapter connectivity")

    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "run":
        cmd_run(args)
    elif args.cmd == "health":
        cmd_health(args)


if __name__ == "__main__":
    main()
