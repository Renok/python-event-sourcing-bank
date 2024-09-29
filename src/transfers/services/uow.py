from __future__ import annotations
import abc
import esdbclient

from transfers import config
from transfers.adapters import repository


class AbstractUnitOfWork(abc.ABC):
    accounts: repository.AbstractAccountsRepository

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


class EventStoreDBUnitOfWork(AbstractUnitOfWork):
    def __enter__(self):
        client = esdbclient.EventStoreDBClient(uri=config.get_esdb_uri())
        self.accounts = repository.AccountEventStoreDBRepository(client)
        return super().__enter__()

    def __exit__(self, *args):
        return super().__exit__()

    def commit(self):
        pass

    def rollback(self):
        pass
