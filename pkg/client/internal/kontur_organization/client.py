from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from pkg.client.client import AsyncHTTPClient


class KonturOrganizationClient(interface.IKonturOrganizationClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            host: str,
            port: int,
            interserver_secret_key: str,
    ):
        logger = tel.logger()
        self.client = AsyncHTTPClient(
            host,
            port,
            prefix="/api/organization",
            use_tracing=True,
            logger=logger,
        )
        self.tracer = tel.tracer()
        self.interserver_secret_key = interserver_secret_key

    async def debit_balance(self, organization_id: int, amount_rub: int) -> None:
        with self.tracer.start_as_current_span(
                "KonturOrganizationClient.debit_balance",
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

