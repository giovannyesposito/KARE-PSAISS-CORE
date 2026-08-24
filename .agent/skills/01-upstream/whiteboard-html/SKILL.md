# SKILL: whiteboard-html

## Descrição

Gera whiteboards visuais interativos no estilo Miro/FigJam como arquivos HTML standalone.
Usado para visualizar artefatos de produto (Lean Inception, PRD, RAID, Sprint Plan, User Story Map etc.)
de forma rica e navegável, sem dependência de ferramentas externas.

## Quando Usar

Ativar quando o usuário pedir:
- "cria um whiteboard"
- "gera um board visual"
- "monta no estilo Miro / FigJam"
- "visualização interativa de [artefato]"
- "board de sticky notes"
- "quadro visual de [artefato]"

---

## Output Padrão

```
_outputs/<context-slug>/<ARTEFATO>_WHITEBOARD.html
```

Exemplos:
- `_outputs/demo-pass/LEAN_INCEPTION_WHITEBOARD.html`
- `_outputs/ini-002/RAID_WHITEBOARD.html`
- `_outputs/ini-003/SPRINT_PLAN_WHITEBOARD.html`

---

## Estrutura HTML Obrigatória

### 1 — `<head>` — CSS Variables

Sempre iniciar com estas variáveis CSS (não alterar os nomes):

```css
:root {
  --yellow: #fef08a;  --yellow-dark: #ca8a04;
  --green:  #bbf7d0;  --green-dark:  #15803d;
  --blue:   #bfdbfe;  --blue-dark:   #1d4ed8;
  --pink:   #fecdd3;  --pink-dark:   #be123c;
  --purple: #e9d5ff;  --purple-dark: #7e22ce;
  --orange: #fed7aa;  --orange-dark: #c2410c;
  --red:    #fca5a5;  --red-dark:    #b91c1c;
  --teal:   #99f6e4;  --teal-dark:   #0f766e;
  --gray:   #e2e8f0;  --gray-dark:   #475569;
  --shadow: 0 4px 12px rgba(0,0,0,0.12);
  --shadow-hover: 0 8px 24px rgba(0,0,0,0.18);
}
```

### 2 — TopBar (sticky, obrigatório)

```html
<div class="topbar">
  <div class="logo">KARE</div>
  <div class="title">[Nome do Board]</div>
  <div class="nav-pills">
    <button class="nav-pill active" onclick="scrollTo(0,'secao1')">Seção 1</button>
    <!-- ... -->
  </div>
  <span class="badge">[Mês Ano]</span>
</div>
```

CSS da topbar:
- Fundo: `#1e293b`
- Logo: `color: #7c3aed; font-weight: 700`
- Nav pills: background `#334155` → hover/active `#7c3aed`

### 3 — Blocker Banner (quando houver bloqueadores críticos)

```html
<div class="blocker">
  <div class="blocker-icon">🚨</div>
  <div>
    <div class="blocker-title">Título do Bloqueador</div>
    <div class="blocker-text">Descrição do impacto e ação necessária</div>
  </div>
</div>
```

CSS: background `linear-gradient(135deg, #fef2f2, #fff7ed)`, border `#fca5a5`

### 4 — Section Label (separadores de conteúdo)

```html
<div class="section-label">📊 Título da Seção</div>
```

CSS: `font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: #64748b`
Linha decorativa: `::after { content:''; flex:1; height:1px; background: #e2e8f0 }`

### 5 — Day Section (para artefatos divididos por dias/fases)

```html
<div id="dia1" class="day-section day-1">
  <div class="day-header">
    <div class="day-num">1</div>
    <div class="day-title">DIA 1 — Nome da Fase</div>
    <div class="day-tip">💡 Dica para o facilitador</div>
  </div>
  <div class="day-body">
    <!-- conteúdo -->
  </div>
</div>
```

Gradientes por número de dia (usar nos `.day-header`):
- Dia 1: `linear-gradient(135deg, #6366f1, #8b5cf6)` — índigo/roxo
- Dia 2: `linear-gradient(135deg, #0891b2, #0e7490)` — ciano/teal
- Dia 3: `linear-gradient(135deg, #16a34a, #15803d)` — verde
- Dia 4: `linear-gradient(135deg, #ea580c, #c2410c)` — laranja
- Dia 5: `linear-gradient(135deg, #dc2626, #b91c1c)` — vermelho

---

## Componentes Disponíveis

### STICKY NOTES — `.sticky`

```html
<div class="stickies-grid">
  <div class="sticky yellow">
    <div class="sticky-label">Categoria</div>
    <div class="sticky-text">Conteúdo do post-it</div>
    <div class="sticky-sub">Nota complementar</div>
  </div>
</div>
```

Cores disponíveis: `yellow` `orange` `red` `green` `blue` `teal` `purple` `pink` `gray`

Uso recomendado:
- `yellow` — dores, problemas identificados
- `orange` — questões financeiras/operacionais
- `red` — críticos, urgentes
- `blue` — suposições técnicas
- `teal` — suposições de negócio/parceiros
- `purple` — hipóteses de modelo/estratégia
- `green` — validações, evidências confirmadas

Hover: `transform: rotate(1deg) translateY(-3px)`

---

### STAT CARDS — `.stat-card`

```html
<div class="stats-row">
  <div class="stat-card sc-b">
    <span class="stat-num">58%</span>
    <div class="stat-desc">dos lares sem streaming</div>
  </div>
</div>
```

Variantes de cor: `sc-b` (azul) | `sc-r` (vermelho) | `sc-y` (amarelo)

---

### VISÃO DO PRODUTO — `.vision-box`

```html
<div class="vision-box">
  <span class="vision-label">Rótulo da Seção</span>
  <strong>Para</strong> [público] <strong>que</strong> [necessidade],
  <strong>o [produto]</strong> é um [categoria] <strong>que</strong> [benefício].
  <strong>Diferente de</strong> [alternativa], <strong>nosso produto</strong> [diferencial].
</div>
```

CSS: `background: linear-gradient(135deg, #ede9fe, #ddd6fe); border: 2px solid #c4b5fd`

---

### QUADRANTE É/NÃO É/FAZ/NÃO FAZ — `.quadrant`

```html
<div class="quadrant">
  <div class="q-cell is">
    <div class="q-header">✅ É</div>
    <div class="q-item">Item 1</div>
  </div>
  <div class="q-cell isnot">
    <div class="q-header">❌ Não É</div>
    <div class="q-item">Item 1</div>
  </div>
  <div class="q-cell does">
    <div class="q-header">🔵 Faz</div>
    <div class="q-item">Item 1</div>
  </div>
  <div class="q-cell doesnot">
    <div class="q-header">⚠️ Não Faz</div>
    <div class="q-item">Item 1</div>
  </div>
</div>
```

Cores dos headers: `is=verde` | `isnot=vermelho` | `does=azul` | `doesnot=amarelo`

---

### PERSONA CARDS — `.persona-card`

```html
<div class="personas-row">
  <div class="persona-card pc-blue">
    <div class="persona-header">
      <div class="p-avatar">👩‍💼</div>
      <div>
        <div class="p-name">Nome da Persona</div>
        <div class="p-role">Papel / Tag</div>
      </div>
    </div>
    <div class="persona-body">
      <div class="persona-row">
        <span class="persona-icon">😣</span>
        <div class="persona-info"><strong>Dor Principal</strong>Descrição</div>
      </div>
    </div>
  </div>
</div>
```

Variantes de header: `pc-blue` | `pc-teal` | `pc-purple` (inline style para outras cores)

---

### JORNADA DO USUÁRIO — `.journey`

```html
<div class="journey">
  <div class="journey-step j-s1">
    <div class="j-bubble">📢</div>
    <div class="j-phase">Fase 1 · Nome</div>
    <div class="j-action">Ação do usuário</div>
    <div class="j-emotion">😮 Emoção</div>
    <div class="j-friction">⚠️ Ponto de atrito (opcional)</div>
  </div>
  <!-- máx 5 steps: j-s1 ... j-s5 -->
</div>
```

Setas entre steps via CSS `::after { content: '→' }`

---

### TABELA DE OBJETIVOS — `.obj-table`

```html
<table class="obj-table">
  <thead><tr><th>#</th><th>Objetivo</th><th>Métrica</th><th>Meta</th><th>Prazo</th></tr></thead>
  <tbody>
    <tr>
      <td><div class="o-num">O1</div></td>
      <td>Descrição do objetivo</td>
      <td><span class="tag kpi">Nome da métrica</span></td>
      <td><span class="tag meta">Valor alvo</span></td>
      <td><span class="tag prazo">Período</span></td>
    </tr>
  </tbody>
</table>
```

---

### CLUSTERS DE FUNCIONALIDADES — `.feat-clusters`

```html
<div class="feat-clusters">
  <div class="cluster-card">
    <div class="cluster-header ca">🔐 Cluster A — Nome</div>
    <div class="cluster-body">
      <div class="feat-row">
        <span class="feat-id">F01</span>
        <div class="feat-text">Descrição<span class="feat-persona">Persona</span></div>
      </div>
    </div>
  </div>
</div>
```

Variantes de header: `ca`=índigo | `cb`=ciano | `cc`=verde | `cd`=roxo

---

### TABELA REVISÃO T/UX/N — `.review-table`

```html
<table class="review-table">
  <thead><tr><th>ID</th><th>Funcionalidade</th><th>Esforço</th><th>Valor Negócio</th><th>Valor UX</th><th>Decisão</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>F01</strong></td>
      <td>Descrição</td>
      <td><span class="badge-e e-m">M</span></td>
      <td>⭐⭐⭐</td><td>⭐⭐⭐</td>
      <td><span class="badge-d d-fazer">✅ Fazer · MVP</span></td>
    </tr>
  </tbody>
</table>
```

Esforço: `e-p`=verde(P) | `e-m`=amarelo(M) | `e-g`=vermelho(G)
Decisão: `d-fazer` | `d-analisar` | `d-descartar`

---

### SEQUENCIADOR — `.seq-table`

```html
<div class="seq-wrapper">
  <table class="seq-table">
    <thead>
      <tr>
        <th class="seq-th-trilha">Trilha</th>
        <th class="seq-th-onda1">🔴 Onda 1 — MVP</th>
        <th class="seq-th-onda2">🟠 Onda 2</th>
        <th class="seq-th-onda3">🟡 Onda 3</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Nome da Trilha</strong></td>
        <td><span class="seq-chip mvp">F01 · Funcionalidade</span></td>
        <td><span class="seq-chip onda2">F06 · Funcionalidade</span></td>
        <td><span class="seq-chip onda3">F12 · Funcionalidade</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

Chips: `mvp`=verde | `onda2`=laranja | `onda3`=amarelo | `tech`=índigo

---

### MVP CANVAS — `.mvp-canvas`

```html
<div class="mvp-canvas">
  <div class="mvp-block mvp-b1">
    <div class="mvp-block-title">🎯 1. Proposta do MVP</div>
    <div class="mvp-item">Conteúdo</div>
  </div>
  <!-- blocos mvp-b1 a mvp-b8, mais mvp-b9 com classe full-row -->
  <div class="mvp-block mvp-b9 full-row">
    <div class="mvp-block-title">⏱️ 9. Custo e Cronograma</div>
  </div>
</div>
```

Grid: `grid-template-columns: 1fr 1fr` — blocos pares sem border-right, `full-row` ocupa 2 colunas.

---

### RISK CARDS — `.risks-grid`

```html
<div class="risks-grid">
  <div class="risk-card">
    <div class="risk-header r-critico">
      <div class="risk-num">R1</div>
      <div class="risk-title">Título do Risco</div>
    </div>
    <div class="risk-body">
      <div class="risk-pills">
        <span class="risk-pill rp-alta">Prob: Alta</span>
        <span class="risk-pill rp-critico">Impacto: Crítico</span>
      </div>
      <div class="risk-mit"><strong>Mitigação</strong>Plano de ação</div>
    </div>
  </div>
</div>
```

Headers: `r-critico`=vermelho | `r-alto`=laranja | `r-medio`=âmbar
Pills de prob: `rp-alta` | `rp-media`
Pills de impacto: `rp-critico` | `rp-alto` | `rp-medio`

---

### PRÓXIMOS PASSOS — `.next-steps`

```html
<div class="next-steps">
  <div class="next-step-card ns-imediato">
    <div class="ns-header">🔴 Imediato (Semana 1–2)</div>
    <div class="ns-body">
      <div class="ns-item">Ação 1</div>
    </div>
  </div>
  <div class="next-step-card ns-curto">
    <div class="ns-header">🟠 Curto Prazo (Semana 3–6)</div>
    <div class="ns-body"><div class="ns-item">Ação 1</div></div>
  </div>
  <div class="next-step-card ns-medio">
    <div class="ns-header">🟢 Médio Prazo (Mês 2–3)</div>
    <div class="ns-body"><div class="ns-item">Ação 1</div></div>
  </div>
</div>
```

Cores: `ns-imediato`=vermelho | `ns-curto`=laranja | `ns-medio`=verde

---

### COMMAND BADGES — `.cmd-badge`

```html
<span class="cmd-badge">/story</span>
<span class="cmd-badge">/risk</span>
```

CSS: `background: #1e293b; color: #7c3aed; font-family: monospace`

---

## JavaScript Obrigatório

Todo whiteboard deve incluir no `<script>`:

```javascript
// Smooth scroll para seções
function scrollTo(x, id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Highlight automático do nav pill conforme scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      document.querySelectorAll('.nav-pill').forEach(p => p.classList.remove('active'));
      const pill = document.querySelector(`.nav-pill[onclick*="${id}"]`);
      if (pill) pill.classList.add('active');
    }
  });
}, { threshold: 0.3 });

['secao1','secao2','secao3','secao4','secao5'].forEach(id => {
  const el = document.getElementById(id);
  if (el) observer.observe(el);
});
```

---

## Footer Obrigatório

```html
<div class="footer">
  Gerado por <strong>KARE Agile Agent</strong> · [@agentes invocados]<br>
  <strong>[Metodologia]</strong> · [Nome do Programa] · PI Planning CLOCK02 26 · [Mês Ano]
</div>
```

---

## Mapeamento: Artefato → Seções do Board

### Lean Inception (5 dias)
1. Certezas de Mercado (stat cards)
2. Dia 1: Visão + É/Não É + Objetivos
3. Dia 2: Personas + Jornada + Suposições
4. Dia 3: Clusters de Funcionalidades + Revisão T/UX/N
5. Dia 4: Sequenciador (regras + swimlane)
6. Dia 5: MVP Canvas + Riscos + Dúvidas + Decisões

### PRD
1. Header do produto (stat cards de contexto)
2. Visão do Produto
3. Personas + Jobs to Be Done
4. Requisitos funcionais (clusters)
5. Critérios de aceite
6. Fora de escopo
7. Métricas de sucesso

### RAID
1. Riscos (risk cards com matriz)
2. Assumptions (sticky notes verdes)
3. Issues em aberto (sticky notes vermelhas)
4. Dependências (fluxo → setas)

### Sprint Plan
1. Sprint Goal (vision box)
2. Backlog priorizado (tabela com esforço/valor)
3. Capacity do time (stat cards)
4. DoR checklist por story
5. Riscos do sprint

### User Story Map
1. Atividades do usuário (swimlane horizontal)
2. Stories por atividade (sticky notes)
3. Priorização por release/sprint (cores por linha)

---

## Arquivo de Referência Completo

O HTML de referência canônico está em:
```
_outputs/demo-pass/LEAN_INCEPTION_WHITEBOARD.html
```

Ao gerar novos boards, usar este arquivo como base estrutural do CSS e copiar os componentes necessários.

---

**Skill Version:** 1.0.0 | **Data:** Maio 2026
**Maintainer:** KARE Agile Agent
