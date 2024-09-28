from uuid import UUID

from transfers.domain import events, exceptions


class Account:
    def __init__(self, account_id: UUID) -> None:
        self.account_id = account_id
        self.balacne: int = 0
        self.version: int = 0
        self.events = []

        self.event_handlers = {
            events.WithdrawnEvent: self._withdraw,
            events.DepositedEvent: self._deposit,
        }

    def _check_amount(self, amount: int) -> None:
        if amount <= 0:
            raise exceptions.NotPositiveAmountTransfer(
                "Transfer amount should be more than 0"
            )

    def create_account(self):
        if self.events:
            raise exceptions.AccountAlreadyExists(
                f"Account {self.account_id} already exists"
            )

        event = events.AccountCreated(account_id=self.account_id)
        self._apply_event(event)

    def withdraw(self, amount: int) -> None:
        self._check_amount(amount)
        if amount > self.balacne:
            raise exceptions.NotEnoughFunds("Not enough funds")

        event = events.WithdrawnEvent(account_id=self.account_id, amount=amount)
        self._apply_event(event)

    def deposit(self, amount: int) -> None:
        self._check_amount(amount)
        event = events.DepositedEvent(account_id=self.account_id, amount=amount)
        self._apply_event(event)

    def _withdraw(self, event: events.WithdrawnEvent) -> None:
        self.balacne -= event.amount

    def _deposit(self, event: events.DepositedEvent) -> None:
        self.balacne += event.amount

    def _apply_event(self, event: events.Event) -> None:
        handler = self.event_handlers.get(type(event), None)
        if handler:
            handler(event)
        self.events.append(event)
        self.version += 1

    def load_from_events(self, events: list[events.Event]) -> None:
        for event in events:
            self._apply_event(event)
