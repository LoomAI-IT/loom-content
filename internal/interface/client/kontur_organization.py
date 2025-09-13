from abc import abstractmethod
from typing import Protocol

from internal import model


class IKonturOrganizationClient(Protocol):
    @abstractmethod
    async def debit_balance(self, organization_id: int, amount_rub: int) -> None: pass