from __future__ import annotations
import abc

from uuid import UUID

from transfers.domain.models import Account
from transfers.adapters.repository import AbstractAccountsRepository


class AbstractUnitOfWork(abc.ABC):
    accounts: AbstractAccountsRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def load_account(self, account_id: UUID) -> Account:
        account = Account(account_id=account_id)
        events = self.accounts.get_events(account_id=account_id)
        account.load_from_events(events)
        return account

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
