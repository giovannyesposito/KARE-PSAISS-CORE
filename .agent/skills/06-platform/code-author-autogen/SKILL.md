---
name: code-author-autogen
description: >
  Ciclo completo TDD assistido via AutoGen: geração de código → execução em
  sandbox → debugging automático → feedback humano (HITL). Suporte a Python,
  TypeScript, Java, Go e Kotlin sem configuração adicional de linguagem.
sprint: 2
agente_destino: "@code-author"
framework: AutoGen
referencia: "https://github.com/microsoft/autogen/blob/0.2/notebook/agentchat_human_feedback.ipynb"
tools:
  - Read
  - Grep
  - Write
  - Edit
  - Bash
triggers:
  - "autogen"
  - "sandbox de execução"
  - "auto debug"
  - "gerar e executar código"
  - "human feedback loop"
  - "TDD assistido"
  - "compilar e testar"
---

# Code Author AutoGen — TDD com Sandbox + HITL

> **Sprint 2 — Desenvolvimento Core** | Framework: AutoGen | Agente: `@code-author`

## Propósito

Ampliar o `@code-author` com capacidade de **executar e depurar código gerado** em
sandbox isolado, iterando automaticamente sobre erros (até max 3 — Loop Guard) antes
de escalar ao humano.

---

## Ciclo de Execução

```
Requisito (US / AC)
       │
       ▼
  [1] Gerar código (LLM)
       │
       ▼
  [2] Executar em sandbox (subprocess / Docker)
       │
    ┌──┴──────────┐
    │  Sucesso?   │
    └──┬──────────┘
       │ NÃO (erro)
       ▼
  [3] Analisar erro + refinar (até 3x → Loop Guard)
       │
       ▼ 3x sem sucesso
  [4] HITL — escalar ao humano com contexto do erro
```

---

## Configuração do Sandbox

### Python / TypeScript / Go (subprocess isolado)

```python
import subprocess, tempfile, os

def executar_codigo(codigo: str, linguagem: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile(suffix=EXT[linguagem], mode='w', delete=False) as f:
        f.write(codigo)
        nome_arquivo = f.name

    try:
        resultado = subprocess.run(
            CMDS[linguagem] + [nome_arquivo],
            capture_output=True, text=True,
            timeout=30,  # timeout de segurança
        )
        sucesso = resultado.returncode == 0
        saida = resultado.stdout if sucesso else resultado.stderr
        return sucesso, saida
    finally:
        os.unlink(nome_arquivo)

EXT = {"python": ".py", "typescript": ".ts", "go": ".go", "java": ".java"}
CMDS = {
    "python": ["python", "-m", "pytest", "-q"],
    "typescript": ["npx", "ts-node", "--transpile-only"],
    "go": ["go", "run"],
    "java": ["java", "-cp", "."]
}
```

---

## Integração com Loop Guard

```python
from loop_guard import get_session_tracker, LoopDetectedError

def gerar_e_executar_com_retry(requisito: str, linguagem: str) -> str:
    tracker = get_session_tracker(f"code-gen-{requisito[:20]}", max_retries=3)
    codigo = llm_gerar_codigo(requisito, linguagem)

    while True:
        try:
            tracker.record("Sandbox.execute", {"lang": linguagem})
        except LoopDetectedError:
            # HITL — não tentar mais, escalar
            return hitl_escalate(requisito, codigo, ultimo_erro)

        sucesso, saida = executar_codigo(codigo, linguagem)
        if sucesso:
            return codigo

        ultimo_erro = saida
        codigo = llm_refinar_codigo(codigo, saida)  # debug + refine
```

---

## Linguagens Suportadas — Stack do Projeto

| Linguagem | Runtime | Casos de Uso |
|---|---|---|
| Python | Python 3.11+ | Scripts de análise, automações KARE |
| TypeScript | Node.js + ts-node | APIs NestJS, frontend React |
| Java | JDK 17 | Kafka Streams, Oracle BRM |
| Kotlin | JVM 17 | Kafka Consumers, microserviços |
| Go | 1.22+ | Microsserviços de alto throughput |

---

## Guardrail — Autorização Obrigatória

> ⛔ **NÍVEL: CRÍTICO** — Esta skill executa código gerado por LLM em processo local.
> **Nenhuma execução pode ocorrer sem autorização explícita de um operador humano.**

### Ativar antes de usar

```powershell
# 1. Verificar status atual
python .agent/scripts/guards/guardrail_gate.py check code-author-autogen

# 2. Autorizar (expira em 60 min)
python .agent/scripts/guards/guardrail_gate.py approve code-author-autogen --reason "TDD para US-XXX — sprint N"

# 3. Revogar manualmente se necessário
python .agent/scripts/guards/guardrail_gate.py revoke code-author-autogen
```

### Integração no código da skill

```python
from guardrail_gate import require_authorization, GuardrailDenied

# Verificar autorização ANTES de qualquer execução de código
try:
    require_authorization("code-author-autogen")
except GuardrailDenied as e:
    print(str(e))  # instrução clara de como autorizar
    sys.exit(1)
```

### Sandbox — Módulos Bloqueados

O processo filho **não pode importar**:
```python
BLOCKED_MODULES = [
    "os", "subprocess", "shutil", "socket",
    "requests", "urllib", "ftplib", "http"
]
# Implementar via importlib.import_module hook ou RestrictedPython
```

### Audit Log

Toda autorização e execução é registrada em:
`.agent/.guardrails/authorizations.jsonl` e `.agent/.guardrails/audit.jsonl`

---

## Critérios de Aceite

- [ ] Código gerado passa em lint sem erros
- [ ] Loop de debug converge em <= 3 iterações
- [ ] Human feedback registrado em ORCHESTRATION_REPORT
- [ ] Suporte confirmado para Python, TypeScript e Java
- [ ] Timeout de sandbox <= 30s por execução
- [ ] **Guardrail verificado: `guardrail_gate.py check code-author-autogen` retorna ✅**
- [ ] **Módulos bloqueados (os, subprocess, shutil, socket) não importáveis no sandbox**
- [ ] **Audit log contém registro da autorização antes da execução**
