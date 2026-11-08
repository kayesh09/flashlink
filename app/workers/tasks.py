import asyncio
from cmath import e

import orjson
from datetime import datetime,timezone
from arq import cron
from arq.connections import RedisSettings
from redis.asyncio import Redis,from_url

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.click_events import ClickEvent
from app.models.link import Link
from sqlalchemy import update
from sqlalchemy.testing.suite.test_reflection import users

from flashlink.app.services.redirect import CLICK_STREAM

CLICK_STREAM = "stream:click"
BATCH_SIZE = 500
CONSUMER= "worker-1 "
GROUP = "click-ingest"
async def ingest_click(ctx) -> int:
    redis:Redis = ctx["redis"]
    try:
        await redis.xgrop_create(CLICK_STREAM,GROUP,id="0",mkstream=True)
    except Exception:
        pass

    raw = await redis.xreadgroup(
        groupname=GROUP,consumername=CONSUMER,
        streams={CLICK_STREAM:">"},count=BATCH_SIZE,block=2000,
    )
    if not raw:
        return 0
    events = []
    counters: dict[str,int] = {}
    ids_to_ack = []
    for _stream,messages in raw:
        for mgs_id,fields in messages:
            try:
                data = orjson.loads(fields[b"d"] if isinstance(
                    next(iter(fields)),bytes) else fields["d"])
                events.append(data)
                counters[data["code"]] = counters.get(data["code"],0)+1
                ids_to_ack.append(mgs_id)
            except Exception:
                pass
    if events:
        async with AsyncSessionLocal() as session:
            codes = list(counters.keys())
            from sqlalchemy import select
            rows = (await session.execute(
                    select(Link.id,Link.short_code).where(
                    Link.short_code.in_(codes))
                )
            ).all()
            code_to_id = {r.short_code:r.id for r in rows}
            session.add_all ([
                ClickEvent(
                    link_id = code_to_id[e["code"]],
                    ip = e.get("ip"),
                    users_agent= e.get("ua"),
                    created_at = datetime.fromisoformat(e["ts"]),


                )
                for e in events if events if e("code") in code_to_id
            ])
            for code ,count in counters.items():
                if code in code_to_id:
                    await session.execute(
                        update(Link).where(Link.id == code_to_id[code])
                        .values(clicks=Link.clicks + count)

                    )
                    await session.commit()

    if ids_to_ack:
        await redis.xack(CLICK_STREAM,GROUP,*ids_to_ack)
        return len(events)
async def snapshot_counters(ctx) -> None:
    pass

class WorkerSettings:
    functions = [ingest_click]
    cron_jobs = [cron(snapshot_counters,hour={0,12})]
    redis_settings = RedisSettings.from_dsn(str(settings.redis_dsn))
    max_jobs= 4
    job_timeout = 30



