from app.repositories.benefit_repository import create_benefit, list_benefits_for_card
from app.repositories.card_repository import create_card, list_cards_for_user, update_performance
from app.repositories.payment_event_repository import (
    create_payment_event,
    list_events_for_merchant,
)
from app.repositories.user_repository import create_user, get_user


def test_user_crud(db):
    user = create_user(db, name="테스트유저")
    assert user.id is not None
    fetched = get_user(db, user.id)
    assert fetched.name == "테스트유저"


def test_card_crud(db):
    user = create_user(db, name="카드유저")
    card = create_card(
        db,
        user_id=user.id,
        card_name="신한카드",
        card_type="신용카드",
        current_performance=100000,
        required_performance=300000,
    )
    assert card.id is not None

    cards = list_cards_for_user(db, user.id)
    assert len(cards) == 1
    assert cards[0].card_name == "신한카드"

    updated = update_performance(db, card, current_performance=430000)
    assert float(updated.current_performance) == 430000


def test_benefit_crud(db):
    create_benefit(
        db, card_name="테스트카드", category="테스트업종", discount_rate=0.10, condition="실적 30만원 이상"
    )
    benefits = list_benefits_for_card(db, "테스트카드")
    assert len(benefits) == 1
    assert float(benefits[0].discount_rate) == 0.10


def test_payment_event_crud(db):
    create_payment_event(db, payment_type="테스트페이", merchant="테스트가맹점", benefit_rate=0.02)
    events = list_events_for_merchant(db, "테스트가맹점")
    assert len(events) == 1
    assert events[0].payment_type == "테스트페이"
