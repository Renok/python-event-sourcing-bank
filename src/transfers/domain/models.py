from uuid import UUID
from typing import Iterable

from transfers.domain import events as events_
from transfers.domain import exceptions


class Account:
    def __init__(self, account_id: UUID) -> None:
        self.account_id = account_id
        self.balacne: int = 0
        self.version: int = 0
        self.commited_events: list = []
        self.uncommited_events: list = []

    @property
    def account_created(self) -> bool:
        return bool(self.events)

    @property
    def events(self) -> list[events_.Event]:
        return self.uncommited_events + self.commited_events

    @staticmethod
    def _check_amount(amount: int) -> None:
        if amount <= 0:
            raise exceptions.NotPositiveAmountTransfer(
                "Transfer amount should be more than zero"
            )

    def create_account(self) -> None:
        if self.account_created:
            raise exceptions.AccountAlreadyExists(
                f"Account {self.account_id} already exists"
            )

        event = events_.AccountCreated(account_id=self.account_id)
        self._process_event(event)

    def withdraw(self, amount: int) -> None:
        self._check_amount(amount)
        if amount > self.balacne:
            raise exceptions.NotEnoughFunds("Not enough funds")

        event = events_.WithdrawnEvent(account_id=self.account_id, amount=amount)
        self._process_event(event)

    def deposit(self, amount: int) -> None:
        self._check_amount(amount)
        event = events_.DepositedEvent(account_id=self.account_id, amount=amount)
        self._process_event(event)

    def _withdraw(self, event: events_.WithdrawnEvent) -> None:
        self.balacne -= event.amount

    def _deposit(self, event: events_.DepositedEvent) -> None:
        self.balacne += event.amount

    def _process_event(self, event: events_.Event) -> None:
        self._apply_event(event)
        self.uncommited_events.append(event)

    def _apply_event(self, event: events_.Event) -> None:
        match type(event):
            case events_.AccountCreated:
                pass
            case events_.WithdrawnEvent:
                self._withdraw(event)
            case events_.DepositedEvent:
                self._deposit(event)
            case _:
                raise ValueError(f"Unknown event: {event}")
        self.version += 1

    def load_from_history(self, events: Iterable[events_.Event]) -> None:
        self.commited_events = list(events)
        for event in events:
            self._apply_event(event)

    def commit_events(self):
        self.commited_events += self.uncommited_events
        self.uncommited_events = []
