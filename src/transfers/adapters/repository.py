import abc
from uuid import UUID

from transfers.domain import events, models


class AbstractAccountsRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, account: models.Account):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, account_id: UUID) -> models.Account:
        raise NotImplementedError

    @abc.abstractmethod
    def add_events(self, account: models.Account, original_version: int):
        raise NotImplementedError

    @abc.abstractmethod
    def get_events(self, account_id: UUID):
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[models.Account]:
        raise NotImplementedError
