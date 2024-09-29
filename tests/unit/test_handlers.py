from uuid import uuid4
from collections import defaultdict


from transfers.domain import commands, models
from transfers.services import handlers
from transfers.adapters.repository import AbstractAccountsRepository
from transfers.services.uow import AbstractUnitOfWork


class FakeAccountsRepository(AbstractAccountsRepository):
    def __init__(self) -> None:
        self.accounts_events = defaultdict(list)

    def add(self, account):
        self.accounts_events[account.account_id].extend(account.uncommited_events)
        account.commit_events()

    def get(self, account_id):
        if account_id not in self.accounts_events:
            return None
        account = models.Account(account_id)
        account_events = self.accounts_events[account_id]
        account.load_from_history(account_events)
        return account

    def list(self):
        pass


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.accounts = FakeAccountsRepository()
        self.commited = False

    def commit(self):
        self.commited = True

    def rollback(self):
        pass


def test_create_account():
    cmd = commands.CreateAccount(account_id=uuid4())
    uow = FakeUnitOfWork()

    handlers.create_account(cmd=cmd, uow=uow)

    assert uow.accounts.get(cmd.account_id)
    assert uow.commited


def test_deposit():
    account_id = uuid4()
    uow = FakeUnitOfWork()

    account = models.Account(account_id=account_id)
    account.create_account()
    uow.accounts.add(account)

    cmd = commands.DepositCommand(account_id=account_id, amount=200)
    handlers.depoist(cmd=cmd, uow=uow)


def test_transfer():
    account_id_from = uuid4()
    account_id_to = uuid4()

    uow = FakeUnitOfWork()

    deposit_amount = 400
    transfer_amount = 200
    account_from = models.Account(account_id=account_id_from)
    account_to = models.Account(account_id=account_id_to)
    account_from.create_account()
    account_to.create_account()
    account_from.deposit(amount=deposit_amount)

    uow.accounts.add(account_from)
    uow.accounts.add(account_to)

    cmd = commands.TransferCommand(
        account_id_from=account_id_from,
        account_id_to=account_id_to,
        amount=transfer_amount,
    )
    handlers.transfer(cmd=cmd, uow=uow)

    account_from = uow.accounts.get(account_id_from)
    account_to = uow.accounts.get(account_id_to)

    assert account_from.balance == deposit_amount - transfer_amount
    assert account_to.balance == transfer_amount


def test_transfer_concurrent():
    pass
