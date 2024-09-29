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
        account = uow.accounts.get(account_id=cmd.account_id)
        account.deposit(cmd.amount)
        uow.accounts.add(account)
        uow.commit()


def transfer(cmd: commands.TransferCommand, uow: AbstractUnitOfWork):
    # TODO use saga / process manager
    with uow:
        account_from = uow.accounts.get(cmd.account_id_from)
        account_to = uow.accounts.get(cmd.account_id_to)

        account_from.withdraw(cmd.amount)
        account_to.deposit(cmd.amount)

        uow.accounts.add(account_from)
        uow.accounts.add(account_to)

        uow.commit()
