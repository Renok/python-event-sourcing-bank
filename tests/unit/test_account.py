import pytest
from uuid import uuid4
from transfers.domain.models import Account
from transfers.domain.events import DepositedEvent, WithdrawnEvent
from transfers.domain.exceptions import NotEnoughFunds, NotPositiveAmountTransfer


def test_sum_match():
    account = Account(uuid4())

    account.create_account()
    account.deposit(400)
    account.withdraw(50)
    account.withdraw(100)
    account.deposit(20)

    assert account.balacne == 270

    assert len(account.events) == 5
    assert account.version == len(account.events)


def test_withdraw_limit():
    account = Account(uuid4())
    account.create_account()
    account.deposit(100)

    with pytest.raises(NotEnoughFunds):
        account.withdraw(200)

    assert len(account.events) == 2
    assert account.version == len(account.events)


def test_negative_deposit():
    account = Account(uuid4())
    account.create_account()

    with pytest.raises(NotPositiveAmountTransfer):
        account.deposit(-10)

    assert len(account.events) == 1
    assert account.version == len(account.events)


def test_negative_withdraw():
    account = Account(uuid4())
    account.create_account()

    with pytest.raises(NotPositiveAmountTransfer):
        account.withdraw(-10)

    assert len(account.events) == 1
    assert account.version == len(account.events)


def test_load_events():
    account_id = uuid4()
    account = Account(account_id)
    account.create_account()

    events = [
        DepositedEvent(account_id=account_id, amount=200),
        WithdrawnEvent(account_id=account_id, amount=100),
    ]
    account.load_from_history(events)
    account.balacne == 100

    assert len(account.events) == 3
    assert account.version == len(account.events)
