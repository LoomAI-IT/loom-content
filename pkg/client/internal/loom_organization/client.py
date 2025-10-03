from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface, model
from pkg.client.client import AsyncHTTPClient


class LoomOrganizationClient(interface.ILoomOrganizationClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            host: str,
            port: int,
            interserver_secret_key: str,
    ):
        self.client = AsyncHTTPClient(
            host,
            port,
            prefix="/api/organization",
            use_tracing=True,
        )
        self.tracer = tel.tracer()
        self.interserver_secret_key = interserver_secret_key

    async def debit_balance(self, organization_id: int, amount_rub: str) -> None:
        with self.tracer.start_as_current_span(
                "LoomOrganizationClient.debit_balance",
                kind=SpanKind.CLIENT,
                attributes={
                    "organization_id": organization_id,
                    "amount_rub": amount_rub,
                }
        ) as span:
            try:
                body = {
                    "organization_id": organization_id,
                    "amount_rub": amount_rub,
                    "interserver_secret_key": self.interserver_secret_key,
                }
                await self.client.post("/balance/debit", json=body)

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def get_organization_by_id(self, organization_id: int) -> model.Organization:
        with self.tracer.start_as_current_span(
                "OrganizationClient.get_organization_by_id",
                kind=SpanKind.CLIENT,
                attributes={
                    "organization_id": organization_id
                }
        ) as span:
            try:
                response = await self.client.get(f"/{organization_id}")
                json_response = response.json()

                span.set_status(Status(StatusCode.OK))
                return model.Organization(**json_response)
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
