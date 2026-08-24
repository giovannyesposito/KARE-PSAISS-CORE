"""Testes para o rerank local e o orçamento de tokens em kare_rag.py (search/ask)."""

FACTORY_DEFAULT_VALUE = "@Kar3Padr4o123"


def _ingest(kare_rag, title, content, type_="concept", symbols=""):
    class Args:
        pass

    a = Args()
    a.title = title
    a.type = type_
    a.context = "global"
    a.file = None
    a.content = content
    a.symbols = symbols
    a.password = FACTORY_DEFAULT_VALUE
    kare_rag.cmd_ingest(a)


def test_rerank_boosts_exact_title_match_above_higher_bm25_content_match(isolated_rag_with_credentials):
    kare_rag, _ = isolated_rag_with_credentials

    results = [
        {"title": "Outro assunto qualquer", "content": "menciona reranking de leve", "symbols": "", "score": -1.5},
        {"title": "Reranking de contexto", "content": "explica o conceito uma vez", "symbols": "", "score": -1.0},
    ]

    kare_rag._rerank(results, "reranking")

    assert results[0]["title"] == "Reranking de contexto"


def test_rerank_is_deterministic_and_stable_for_no_term_match(isolated_rag_with_credentials):
    kare_rag, _ = isolated_rag_with_credentials

    results = [
        {"title": "A", "content": "x", "symbols": "", "score": -1.0},
        {"title": "B", "content": "y", "symbols": "", "score": -3.0},
    ]

    kare_rag._rerank(results, "termo que não aparece em nenhum")

    # sem boost de nenhum lado, ordena só por abs(score) — maior primeiro
    assert [r["title"] for r in results] == ["B", "A"]


def test_apply_token_budget_returns_all_when_no_budget_set(isolated_rag_with_credentials):
    kare_rag, _ = isolated_rag_with_credentials

    results = [{"title": "A", "content": "x" * 400, "symbols": ""}] * 3
    assert kare_rag._apply_token_budget(results, None) == results


def test_apply_token_budget_drops_least_relevant_tail_first(isolated_rag_with_credentials):
    kare_rag, _ = isolated_rag_with_credentials

    # cada item ~= 25 tokens (100 chars // 4); já ordenados por relevância desc
    results = [
        {"title": f"Item {i}", "content": "x" * 100, "symbols": ""}
        for i in range(5)
    ]

    budgeted = kare_rag._apply_token_budget(results, max_tokens=60)

    assert len(budgeted) < len(results)
    # mantém o prefixo mais relevante, na mesma ordem
    assert [r["title"] for r in budgeted] == [r["title"] for r in results[: len(budgeted)]]


def test_apply_token_budget_always_keeps_at_least_the_first_item(isolated_rag_with_credentials):
    kare_rag, _ = isolated_rag_with_credentials

    results = [{"title": "Único item grande", "content": "x" * 4000, "symbols": ""}]
    budgeted = kare_rag._apply_token_budget(results, max_tokens=1)

    assert len(budgeted) == 1


def test_cmd_search_respects_max_tokens_end_to_end(isolated_rag_with_credentials, capsys):
    kare_rag, _ = isolated_rag_with_credentials

    for i in range(4):
        _ingest(kare_rag, f"Contexto de orcamento {i}", "conteudo relevante sobre orcamento " * 20)

    capsys.readouterr()  # descarta os prints de cmd_ingest, mantém só a saída de cmd_search abaixo

    class Args:
        pass

    a = Args()
    a.query = "orcamento"
    a.limit = 10
    a.db = "perene"
    a.layer = "all"
    a.json = True
    a.max_tokens = 30

    kare_rag.cmd_search(a)
    out = capsys.readouterr().out
    import json as _json
    payload = _json.loads(out)

    assert len(payload) < 4
    assert len(payload) >= 1
