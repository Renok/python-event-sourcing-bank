from uuid import uuid4, UUID
from transfers.domain import events, commands, models
from transfers.services import handlers
from transfers.adapters.repository import AbstractAccountsRepository
from transfers.services.uow import AbstractUnitOfWork


class FakeAccountsRepository(AbstractAccountsRepository):
    def __init__(self, accounts: list[models.Account]) -> None:
        self.accounts = accounts

    def add(self, account: models.Account):
        self.accounts.append(account)

    def get(self, account_id: UUID):
        return next(
            (account for account in self.accounts if account.account_id == account_id),
            None,
        )

    def list(self):
        return self.accounts

    def add_events(self, account: models.Account, original_version: int):
        stored_account = self.get(account.account_id)
        stored_account.events.extend(account.events[original_version:])

    def get_events(self, account_id: events.UUID):
        account = self.get(account_id)
        return account.events


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.accounts = FakeAccountsRepository([])
        self.commited = False

    def commit(self):
        self.commited = True

    def rollback(self):
        pass


def test_create_account():
    cmd = commands.CreateAccount(account_id=uuid4())
    uow = FakeUnitOfWork()

    handlers.create_account(cmd=cmd, uow=uow)

    assert uow.accounts.get(cmd.account_id) is not None
    assert uow.commited


def test_deposit():
    cmd = commands.CreateAccount(account_id=uuid4())
    uow = FakeUnitOfWork()

    account_id = handlers.create_account(cmd=cmd, uow=uow)

    cmd = commands.DepositCommand(account_id=account_id, amount=100)
    handlers.depoist(cmd=cmd, uow=uow)

    account = uow.load_account(account_id)
    assert account.account_id == account_id
    assert account.balacne == 100


def test_transfer():
    uow = FakeUnitOfWork()

    cmd = commands.CreateAccount(account_id=uuid4())
    account_id_from = handlers.create_account(cmd=cmd, uow=uow)

    cmd = commands.CreateAccount(account_id=uuid4())
    account_id_to = handlers.create_account(cmd=cmd, uow=uow)

    cmd = commands.DepositCommand(account_id=account_id_from, amount=200)
    handlers.depoist(cmd=cmd, uow=uow)

    cmd = commands.TransferCommand(
        account_id_from=account_id_from, account_id_to=account_id_to, amount=100
    )
    handlers.transfer(cmd=cmd, uow=uow)

    account_from = uow.load_account(account_id_from)
    account_to = uow.load_account(account_id_to)

    assert account_from.balacne == 100
    assert account_to.balacne == 100
