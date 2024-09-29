from dataclasses import dataclass


@dataclass
class Event:
    pass


@dataclass
class AccountCreated(Event):
    pass


@dataclass
class DepositedEvent(Event):
    amount: int


@dataclass
class WithdrawnEvent(Event):
    amount: int
