import abc
from uuid import UUID

from transfers.domain import models


class AbstractAccountsRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, account: models.Account):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, account_id: UUID) -> models.Account:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[models.Account]:
        raise NotImplementedError
