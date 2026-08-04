import app.services.llm_explainer as llm_explainer
from app.core.config import settings
from app.services.llm_explainer import _fallback_reason, generate_recommendation_reason
from app.services.rule_engine import Candidate


def make_candidate(**overrides) -> Candidate:
    base = dict(
        card_name="신한카드",
        payment_type="네이버페이",
        performance_met=True,
        benefit_category="올리브영",
        benefit_rate=0.10,
        discount_amount=4830,
        event_rate=0.02,
        event_amount=966,
        total_saving=5796,
    )
    base.update(overrides)
    return Candidate(**base)


def test_fallback_used_when_no_api_key(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "")
    reason = generate_recommendation_reason("올리브영", "뷰티", 48300, make_candidate())
    assert "신한카드" in reason
    assert "10%" in reason
    assert "네이버페이" in reason


def test_llm_success_path_used_when_key_present(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "fake-key")
    monkeypatch.setattr(llm_explainer, "_call_llm", lambda prompt: "LLM generated reason.")
    reason = generate_recommendation_reason("올리브영", "뷰티", 48300, make_candidate())
    assert reason == "LLM generated reason."


def test_llm_failure_falls_back_to_rule_based_string(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "fake-key")

    def _raise(prompt: str) -> str:
        raise RuntimeError("network down")

    monkeypatch.setattr(llm_explainer, "_call_llm", _raise)
    reason = generate_recommendation_reason("올리브영", "뷰티", 48300, make_candidate())
    assert "신한카드" in reason
    assert "네이버페이" in reason


def test_fallback_mentions_unmet_performance():
    top = make_candidate(performance_met=False, discount_amount=0, benefit_rate=0.0)
    reason = _fallback_reason("올리브영", top)
    assert "실적 조건을 채우지 못해" in reason


def test_fallback_omits_payment_sentence_when_no_event():
    top = make_candidate(payment_type="카카오페이", event_rate=0.0, event_amount=0, total_saving=4830)
    reason = _fallback_reason("올리브영", top)
    assert "카카오페이" not in reason
