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

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
