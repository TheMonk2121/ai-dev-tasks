from __future__ import annotations

from tests.factories import make_case_result, make_eval_run


def test_factories_smoke():
    cr = make_case_result()
    assert cr.id and cr.retrieval_snapshot and cr.retrieved_context
    er = make_eval_run()
    assert er.profile and er.reranker
