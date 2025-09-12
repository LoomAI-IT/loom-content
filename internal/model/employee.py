from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum



class EmployeeRole(Enum):
    ADMIN = "админ"
    MODERATOR = "модератор"
    EMPLOYEE = "сотрудник"

@dataclass
class Employee:
    id: int
    organization_id: int
    account_id: int
    invited_from_employee_id: int

    required_moderation: bool
    autoposting_permission: bool
    add_employee_permission: bool
    edit_employee_perm_permission: bool
    top_up_balance_permission: bool
    sign_up_social_net_permission: bool

    name: str
    role: EmployeeRole

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['Employee']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                invited_from_employee_id=row.invited_from_employee_id,
                account_id=row.account_id,
                required_moderation=row.required_moderation,
                autoposting_permission=row.autoposting_permission,
                add_employee_permission=row.add_employee_permission,
                edit_employee_perm_permission=row.edit_employee_perm_permission,
                top_up_balance_permission=row.top_up_balance_permission,
                sign_up_social_net_permission=row.sign_up_social_net_permission,
                name=row.name,
                role=EmployeeRole(row.role),
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "invited_from_employee_id": self.invited_from_employee_id,
            "account_id": self.account_id,
            "required_moderation": self.required_moderation,
            "autoposting_permission": self.autoposting_permission,
            "add_employee_permission": self.add_employee_permission,
            "edit_employee_perm_permission": self.edit_employee_perm_permission,
            "top_up_balance_permission": self.top_up_balance_permission,
            "sign_up_social_net_permission": self.sign_up_social_net_permission,
            "name": self.name,
            "role": self.role.value,
            "created_at": self.created_at.isoformat()
        }