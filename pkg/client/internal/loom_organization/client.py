from contextvars import ContextVar

from opentelemetry.trace import SpanKind

from internal import interface, model
from pkg.client.client import AsyncHTTPClient
from pkg.trace_wrapper import traced_method


class LoomOrganizationClient(interface.ILoomOrganizationClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            host: str,
            port: int,
            interserver_secret_key: str,
            log_context: ContextVar[dict],
    ):
        self.client = AsyncHTTPClient(
            host,
            port,
            prefix="/api/organization",
            use_tracing=True,
            log_context=log_context
        )
        self.tracer = tel.tracer()
        self.interserver_secret_key = interserver_secret_key

    @traced_method(SpanKind.CLIENT)
    async def debit_balance(self, organization_id: int, amount_rub: str) -> None:
        body = {
            "organization_id": organization_id,
            "amount_rub": amount_rub,
            "interserver_secret_key": self.interserver_secret_key,
        }
        await self.client.post("/balance/debit", json=body)

    @traced_method(SpanKind.CLIENT)
    async def get_organization_by_id(self, organization_id: int) -> model.Organization:
        response = await self.client.get(f"/{organization_id}")
        json_response = response.json()

        return model.Organization(**json_response)

    @traced_method(SpanKind.CLIENT)
    async def get_cost_multiplier(self, organization_id: int) -> model.CostMultiplier:
        response = await self.client.get(f"/{organization_id}/cost-multiplier")
        json_response = response.json()

        return model.CostMultiplier(**json_response)
