from transfers.domain import models, commands, exceptions
from transfers.services.uow import AbstractUnitOfWork


def create_account(cmd: commands.CreateAccount, uow: AbstractUnitOfWork):
    with uow:
        account = uow.accounts.get(cmd.account_id)
        if account is not None:
            raise exceptions.AccountAlreadyExists(
                f"Account {cmd.account_id} already exists"
            )
        account = models.Account(account_id=cmd.account_id)
        account.create_account()
        uow.accounts.add(account)
        uow.commit()

    return account.account_id


def depoist(cmd: commands.DepositCommand, uow: AbstractUnitOfWork):
    with uow:
        account = uow.load_account(account_id=cmd.account_id)
        original_version = account.version
        account.deposit(cmd.amount)
        uow.accounts.add_events(account, original_version)
        uow.commit()


def transfer(cmd: commands.TransferCommand, uow: AbstractUnitOfWork):
    with uow:
        account_from = uow.load_account(cmd.account_id_from)
        account_to = uow.load_account(cmd.account_id_to)

        account_from_original_version = account_from.version
        account_to_original_version = account_to.version

        account_from.withdraw(cmd.amount)
        account_to.deposit(cmd.amount)

        uow.accounts.add_events(account_from, account_from_original_version)
        uow.accounts.add_events(account_to, account_to_original_version)

        uow.commit()
