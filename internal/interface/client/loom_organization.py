from abc import abstractmethod
from typing import Protocol

from internal import model


class ILoomOrganizationClient(Protocol):
    @abstractmethod
    async def debit_balance(self, organization_id: int, amount_rub: str) -> None: pass