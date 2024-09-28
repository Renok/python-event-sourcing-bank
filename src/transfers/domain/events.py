from dataclasses import dataclass
from uuid import UUID


@dataclass
class Event:
    account_id: UUID


@dataclass
class AccountCreated(Event):
    pass


@dataclass
class DepositedEvent(Event):
    amount: int


@dataclass
class WithdrawnEvent(Event):
    amount: int
