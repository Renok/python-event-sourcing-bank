import pytest
from uuid import uuid4
from transfers.domain import models, exceptions, events


def test_sum_match():
    account = models.Account(uuid4())

    account.create_account()
    account.deposit(400)
    account.withdraw(50)
    account.withdraw(100)
    account.deposit(20)

    assert account.balance == 270

    assert len(account.events) == 5
    assert account.version == len(account.events)


def test_withdraw_limit():
    account = models.Account(uuid4())
    account.create_account()
    account.deposit(100)

    with pytest.raises(exceptions.NotEnoughFunds):
        account.withdraw(200)

    assert len(account.events) == 2
    assert account.version == len(account.events)


def test_negative_deposit():
    account = models.Account(uuid4())
    account.create_account()

    with pytest.raises(exceptions.NotPositiveAmountTransfer):
        account.deposit(-10)

    assert len(account.events) == 1
    assert account.version == len(account.events)


def test_negative_withdraw():
    account = models.Account(uuid4())
    account.create_account()

    with pytest.raises(exceptions.NotPositiveAmountTransfer):
        account.withdraw(-10)

    assert len(account.events) == 1
    assert account.version == len(account.events)


def test_load_events():
    account_id = uuid4()
    account = models.Account(account_id)
    account.create_account()

    history_events = [
        events.DepositedEvent(amount=200),
        events.WithdrawnEvent(amount=100),
    ]
    account.load_from_history(history_events)
    account.balance == 100

    assert len(account.events) == 3
    assert account.version == len(account.events)
