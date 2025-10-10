from datetime import datetime, timezone, timedelta


def to_msk(dt: datetime) -> datetime | None:
    return dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=3))) if dt else None