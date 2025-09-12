from abc import abstractmethod
from typing import Protocol

from fastapi.responses import JSONResponse

from internal import model


class IEmployeeController(Protocol):
    @abstractmethod
    async def create_employee(
            self,
            organization_id: int,
            invited_from_employee_id: int,
            account_id: int,
            name: str,
            role: model.EmployeeRole
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_employee_by_id(self, employee_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_employees_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def update_employee_permissions(
            self,
            employee_id: int,
            required_moderation: bool = None,
            autoposting_permission: bool = None,
            add_employee_permission: bool = None,
            edit_employee_perm_permission: bool = None,
            top_up_balance_permission: bool = None,
            sign_up_social_net_permission: bool = None
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def update_employee_role(
            self,
            employee_id: int,
            role: model.EmployeeRole
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_employee(self, employee_id: int) -> JSONResponse:
        pass


class IEmployeeService(Protocol):
    @abstractmethod
    async def create_employee(
            self,
            organization_id: int,
            invited_from_employee_id: int,
            account_id: int,
            name: str,
            role: model.EmployeeRole
    ) -> int:
        pass

    @abstractmethod
    async def get_employee_by_id(self, employee_id: int) -> model.Employee:
        pass

    @abstractmethod
    async def get_employees_by_organization(self, organization_id: int) -> list[model.Employee]:
        pass

    @abstractmethod
    async def update_employee_permissions(
            self,
            employee_id: int,
            required_moderation: bool = None,
            autoposting_permission: bool = None,
            add_employee_permission: bool = None,
            edit_employee_perm_permission: bool = None,
            top_up_balance_permission: bool = None,
            sign_up_social_net_permission: bool = None
    ) -> None:
        pass

    @abstractmethod
    async def update_employee_role(
            self,
            employee_id: int,
            role: model.EmployeeRole
    ) -> None:
        pass

    @abstractmethod
    async def delete_employee(self, employee_id: int) -> None:
        pass

    @abstractmethod
    async def check_employee_permission(
            self,
            employee_id: int,
            permission_type: str
    ) -> bool:
        pass


class IEmployeeRepo(Protocol):
    @abstractmethod
    async def create_employee(
            self,
            organization_id: int,
            invited_from_employee_id: int,
            account_id: int,
            name: str,
            role: model.EmployeeRole,
            required_moderation: bool = False,
            autoposting_permission: bool = False,
            add_employee_permission: bool = False,
            edit_employee_perm_permission: bool = False,
            top_up_balance_permission: bool = False,
            sign_up_social_net_permission: bool = False
    ) -> int:
        pass

    @abstractmethod
    async def get_employee_by_id(self, employee_id: int) -> list[model.Employee]:
        pass

    @abstractmethod
    async def get_employee_by_tg_user_id(self, tg_user_id: int) -> list[model.Employee]:
        pass

    @abstractmethod
    async def get_employees_by_organization(self, organization_id: int) -> list[model.Employee]:
        pass

    @abstractmethod
    async def update_employee_permissions(
            self,
            employee_id: int,
            required_moderation: bool = None,
            autoposting_permission: bool = None,
            add_employee_permission: bool = None,
            edit_employee_perm_permission: bool = None,
            top_up_balance_permission: bool = None,
            sign_up_social_net_permission: bool = None
    ) -> None:
        pass

    @abstractmethod
    async def update_employee_role(
            self,
            employee_id: int,
            role: model.EmployeeRole
    ) -> None:
        pass

    @abstractmethod
    async def delete_employee(self, employee_id: int) -> None:
        pass