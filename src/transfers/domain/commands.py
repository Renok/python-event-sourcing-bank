from uuid import UUID
from dataclasses import dataclass


@dataclass
class Command:
    pass


@dataclass
class CreateAccount(Command):
    account_id: UUID


@dataclass
class DepositCommand(Command):
    account_id: UUID
    amount: int


@dataclass
class TransferCommand(Command):
    account_id_from: UUID
    account_id_to: UUID
    amount: int
