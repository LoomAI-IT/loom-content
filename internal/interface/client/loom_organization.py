from abc import abstractmethod
from typing import Protocol

from internal import model


class ILoomOrganizationClient(Protocol):
    @abstractmethod
    async def debit_balance(self, organization_id: int, amount_rub: str) -> None: pass

    @abstractmethod
    async def get_organization_by_id(self, organization_id: int) -> model.Organization: pass

    @abstractmethod
    async def get_cost_multiplier(self, organization_id: int) -> model.CostMultiplier: pass