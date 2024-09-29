import abc
import json
import esdbclient

from uuid import UUID
from dataclasses import asdict

from transfers.domain import models, events


class AbstractAccountsRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, account: models.Account) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, account_id: UUID) -> models.Account:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[models.Account]:
        raise NotImplementedError


class AccountEventStoreDBRepository(AbstractAccountsRepository):
    def __init__(self, client: esdbclient.EventStoreDBClient) -> None:
        self._client = client

    def add(self, account):
        events_to_append = [
            self._map_domain_event_to_eventstore_event(event)
            for event in account.uncommited_events
        ]
        self._client.append_to_stream(
            stream_name=f"account-{account.account_id}",
            current_version=esdbclient.StreamState.ANY,
            events=events_to_append,
        )
        account.commit_events()

    def get(self, account_id):
        domain_events = [
            self._map_eventstore_event_to_domain_event(event)
            for event in self._client.get_stream(f"account-{account_id}")
        ]
        account = models.Account(account_id=account_id)
        account.load_from_history(domain_events)
        return account

    def list(self):
        raise NotImplementedError

    @staticmethod
    def _map_domain_event_to_eventstore_event(
        event: events.Event,
    ) -> esdbclient.NewEvent:
        """Map a domain event to an eventstore event.

        :param event: the domain event to map
        :return: an eventstore event that can be persisted in EventStoreDB
        """
        return esdbclient.NewEvent(
            type=event.__class__.__name__,
            data=json.dumps(asdict(event)).encode("utf-8"),
        )

    @staticmethod
    def _map_eventstore_event_to_domain_event(
        event: esdbclient.RecordedEvent,
    ) -> events.Event:
        """Map an eventstore event to a domain event.

        :param event: the eventstore event to map
        :return: the equivalent domain event
        """
        EventClass = getattr(events, event.type)
        data = json.loads(event.data.decode("utf-8"))
        return EventClass(**data)
