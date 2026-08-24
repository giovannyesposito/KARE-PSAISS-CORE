---
name: svg-draw-diagrams
description: >
  Gera diagramas SVG dinâmicos a partir de descrições YAML, com suporte a ícones customizados ou formas geométricas básicas. Use quando precisar criar diagramas arquiteturais visuais, representar componentes com ícones, gerar blueprints de arquitetura, fluxogramas ou diagramas C4 Model.
version: 0.1.0
priority: NORMAL
allowed-tools: Read, Write, Edit, Bash
---
# SVG Diagram Generator

Skill dedicada a gerar diagramas SVG dinâmicos e profissionais a partir de descrições em formato YAML. Suporta ícones customizados (SVG) ou formas geométricas básicas.

---

## 1. Visão Geral

### Problema
Diagramas criados em ferramentas visuais (Figma, Draw.io, etc) não são versionáveis, difíceis de manter sincronizados com o código, e não permitem automação.

### Solução
Um pipeline Python que:
1. **Planeja**: Converte requisitos em um arquivo YAML descritivo
2. **Valida**: Verifica estrutura, assets disponíveis e relacionamentos
3. **Renderiza**: Gera SVG otimizado com layout automático

### Características

- ✅ **Declarativo**: Descreva o diagrama em YAML, não coordenadas manualmente
- ✅ **Extensível**: Use seus próprios ícones SVG na pasta `assets/`
- ✅ **Versionável**: YAML + SVG são text-based, perfeitos para Git
- ✅ **Automático**: Layout inteligente com algoritmos de posicionamento
- 🎨 **Profissional**: Setas, labels, cores e estilos customizáveis

---

## 2. Instalação

### Dependências Python

```bash
pip install -r .agent/skills/03-architecture/svg-draw-diagrams/scripts/requirements.txt
```

**Bibliotecas utilizadas:**
- `PyYAML` — Parser YAML
- `svgwrite` — Geração de SVG programática
- `pygraphviz` (opcional) — Layout automático avançado

---

## 3. Workflow Completo

### Fase 1: Planejamento (YAML)

```bash
python .agent/skills/03-architecture/svg-draw-diagrams/scripts/yaml_planner.py --interactive
```

**Perguntas feitas ao usuário:**
1. Quer usar ícones customizados (`assets/`) ou formas básicas?
2. Tipo de diagrama: `architecture` | `flow` | `component` | `sequence`
3. Orientação: `horizontal` | `vertical` | `hierarchical`
4. Título do diagrama
5. Componentes principais (lista)

**Output:** `diagram-plan.yml`

---

### Fase 2: Edição do YAML (Opcional)

Edite manualmente o YAML gerado para ajustar posições, cores, labels, etc.

```yaml
metadata:
  title: "Sistema de Pagamentos - Arquitetura Macro"
  type: architecture
  orientation: horizontal
  dimensions:
    width: 1200
    height: 800

components:
  - id: checkout-bff
    label: "Checkout BFF"
    type: service
    icon: assets/microservice-icon.svg  # ou "rectangle", "circle", etc
    color: "#4A90E2"
    position: auto

  - id: payment-orchestrator
    label: "Payment Orchestrator"
    type: service
    icon: rectangle
    color: "#E94B3C"

connections:
  - from: checkout-bff
    to: payment-orchestrator
    label: "POST /payments"
    style: solid
    color: "#333333"
```

---

### Fase 3: Renderização (Python → SVG)

```bash
python .agent/skills/03-architecture/svg-draw-diagrams/scripts/svg_diagram_generator.py diagram-plan.yml -o output.svg
```

**Argumentos:**

| Argumento | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `input` | positional | — | Arquivo YAML com o plano |
| `-o`, `--output` | opcional | `diagram.svg` | Arquivo SVG de saída |
| `--validate-only` | flag | `False` | Apenas valida YAML sem gerar SVG |
| `--verbose` | flag | `False` | Mostra log detalhado |
| `--no-auto-layout` | flag | `False` | Desabilita layout automático |

---

## 4. Usando Ícones Customizados

### Estrutura da Pasta `assets/`

```
.agent/skills/03-architecture/svg-draw-diagrams/assets/
├── microservice-icon.svg
├── database-icon.svg
├── queue-icon.svg
└── external-system-icon.svg
```

### Regras para Assets

1. **Formato**: Deve ser SVG válido
2. **Viewbox**: Deve ter atributo `viewBox` definido
3. **Dimensões**: Recomendado 64x64 ou 128x128
4. **Cores**: Use classes CSS ou atributos `fill` editáveis
5. **Nomeação**: `kebab-case.svg`

---

## 5. Tipos de Diagramas

### 5.1 Architecture Diagram

```yaml
metadata:
  type: architecture
  orientation: horizontal
```

Usa retângulos para serviços, cilindros para databases, nuvens para sistemas externos, setas direcionais para comunicação.

### 5.2 Flow Diagram (Fluxograma)

```yaml
metadata:
  type: flow
  orientation: vertical
```

Usa retângulos para processos, losangos para decisões, círculos para início/fim.

### 5.3 Component Diagram

```yaml
metadata:
  type: component
  orientation: hierarchical
```

Usa caixas aninhadas, interfaces (portas), dependências entre componentes.

### 5.4 Sequence Diagram

```yaml
metadata:
  type: sequence
  orientation: vertical
```

Usa linhas de vida verticais, setas horizontais com labels, blocos de ativação.

### 5.5 C4 Model Diagrams

Suporta os 4 níveis estáticos + diagramas de suporte:

| Tipo YAML | Nível | Audiência |
|-----------|-------|-----------|
| `c4-context` | 1 – System Context | Todos |
| `c4-container` | 2 – Container | Arquitetos, devs, ops |
| `c4-component` | 3 – Component | Arquitetos e desenvolvedores |
| `c4-landscape` | N/A – System Landscape | Todos |
| `c4-dynamic` | N/A – Dynamic | Arquitetos e desenvolvedores |
| `c4-deployment` | N/A – Deployment | DevOps e Ops |

```yaml
metadata:
  type: c4-container
  level: 2
```

#### Paleta de Elementos C4

| Elemento | Fill interno | Fill externo |
|----------|-------------|-------------|
| `person` | #1168BD | #999999 |
| `software_system` | #1168BD | #999999 |
| `container` | #438DD5 | — |
| `component` | #85BBF0 | — |
| `node` | #FFFFFF stroke #888888 dashed | — |

Use `external: true` para elementos externos (cor cinza).

#### YAML Schema C4 — Exemplo Internet Banking

```yaml
metadata:
  title: "Container Diagram for Internet Banking System"
  type: c4-container
  dimensions:
    width: 1400
    height: 900
  show_legend: true

elements:
  - id: customer
    kind: person
    label: "Personal Banking Customer"
    description: "A customer of the bank, with personal bank accounts."
    external: false

  - id: web-app
    kind: container
    label: "Web Application"
    technology: "Java and Spring MVC"
    description: "Delivers the static content and the Internet banking SPA."
    parent: boundary-ibs

  - id: api-app
    kind: container
    label: "API Application"
    technology: "Java and Spring MVC"
    description: "Provides Internet banking functionality via a JSON/HTTPS API."
    parent: boundary-ibs

  - id: database
    kind: container
    label: "Database"
    technology: "Oracle Database Schema"
    description: "Stores user registration information, hashed credentials."
    shape: cylinder
    parent: boundary-ibs

  - id: email-system
    kind: software_system
    label: "E-mail System"
    description: "The internal Microsoft Exchange e-mail system."
    external: true

boundaries:
  - id: boundary-ibs
    label: "Internet Banking System"
    style: dashed

relationships:
  - from: customer
    to: web-app
    label: "Visits using"
    protocol: "HTTPS"
    style: solid
  - from: api-app
    to: database
    label: "Reads from and writes to"
    protocol: "JDBC"
    style: solid
  - from: api-app
    to: email-system
    label: "Sends e-mails using"
    protocol: "SMTP"
    style: dashed
```

---

## 6. Exemplos Prontos

Ver pasta `examples/`:

```bash
# Diagrama simples
python .agent/skills/03-architecture/svg-draw-diagrams/scripts/svg_diagram_generator.py \
  .agent/skills/03-architecture/svg-draw-diagrams/examples/simple-diagram.yml -o simple.svg

# C4 Container Banking
python .agent/skills/03-architecture/svg-draw-diagrams/scripts/svg_diagram_generator.py \
  .agent/skills/03-architecture/svg-draw-diagrams/examples/c4-container-banking.yml -o c4.svg
```

---

## 7. Formatação Avançada

### Estilos de Conexão

```yaml
connections:
  - from: a
    to: b
    style: solid        # —————→
  - from: c
    to: d
    style: dashed       # - - - →
  - from: e
    to: f
    style: dotted       # · · · →
  - from: g
    to: h
    style: bidirectional  # ←——→
```

### Grupos e Containers

```yaml
groups:
  - id: vpc
    label: "AWS VPC"
    style: dashed-box
    color: "#FF9900"
    contains: [service-a, service-b]
```

### Anotações

```yaml
annotations:
  - target: service-a
    text: "Handles 10k req/s"
    position: top
  - target: database
    text: "Primary: RDS Multi-AZ"
    position: bottom
```

---

## 8. Troubleshooting

**Asset not found:** Verifique se o arquivo existe em `assets/` e o caminho no YAML está correto.

**Invalid YAML syntax:** Valide o arquivo:
```bash
python -c "import yaml; yaml.safe_load(open('diagram.yml'))"
```

**Diagrama não renderiza corretamente:**
- Posições sobrepostas → use `position: auto`
- IDs duplicados → cada componente deve ter ID único
- Conexões inválidas → `from` e `to` devem referenciar IDs existentes

---

## 9. Integração com Documentação

```bash
# Gerar SVG e adicionar ao README de arquitetura
python .agent/skills/03-architecture/svg-draw-diagrams/scripts/svg_diagram_generator.py \
  architecture-macro.yml -o docs/architecture/macro-blueprint.svg

echo "![Macro Architecture](macro-blueprint.svg)" >> docs/architecture/README.md
```

---

## 10. Referências

- Templates: `.agent/skills/03-architecture/svg-draw-diagrams/templates/`
- Exemplos: `.agent/skills/03-architecture/svg-draw-diagrams/examples/`
- Ícones gratuitos: [Lucide](https://lucide.dev/), [Devicon](https://devicon.dev/)
