import asyncio
import orjson
from datetime import datetime
from redis.asyncio import from_url
from sqlalchemy import select, update

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.click_event import ClickEvent
from app.models.link import Link

CLICK_STREAM = "stream:clicks"
GROUP = "click-ingest"
CONSUMER = "worker-1"
BATCH_SIZE = 500


async def main():
    redis = from_url(str(settings.redis_dsn), decode_responses=True)

    # Create the consumer group so we can track which messages we've read
    try:
        await redis.xgroup_create(CLICK_STREAM, GROUP, id="0", mkstream=True)
        print("Created consumer group.")
    except Exception:
        pass  # Group already exists, which is fine

    print("Worker started. Listening for clicks...")

    while True:
        try:
            # Block for 2 seconds waiting for new clicks
            raw = await redis.xreadgroup(
                groupname=GROUP, consumername=CONSUMER,
                streams={CLICK_STREAM: ">"}, count=BATCH_SIZE, block=2000,
            )

            if not raw:
                continue

            events = []
            counters = {}
            ids_to_ack = []

            for _stream, messages in raw:
                for msg_id, fields in messages:
                    try:
                        data = orjson.loads(fields["d"])
                        events.append(data)
                        counters[data["code"]] = counters.get(data["code"], 0) + 1
                        ids_to_ack.append(msg_id)
                    except Exception:
                        pass  # Ignore broken messages

            if events:
                async with AsyncSessionLocal() as session:
                    # Resolve short codes to link IDs
                    codes = list(counters.keys())
                    res = await session.execute(
                        select(Link.id, Link.short_code).where(Link.short_code.in_(codes))
                    )
                    rows = res.all()
                    code_to_id = {r.short_code: r.id for r in rows}

                    click_objs = []
                    for e in events:
                        if e["code"] in code_to_id:
                            click_objs.append(ClickEvent(
                                link_id=code_to_id[e["code"]],
                                ip=e.get("ip"),
                                user_agent=e.get("ua"),
                                created_at=datetime.fromisoformat(e["ts"])
                            ))

                    if click_objs:
                        session.add_all(click_objs)

                    # Update the total click counter on the links table
                    for code, count in counters.items():
                        if code in code_to_id:
                            await session.execute(
                                update(Link).where(Link.id == code_to_id[code]).values(clicks=Link.clicks + count)
                            )

                    await session.commit()
                    print(f"Processed {len(events)} clicks.")

            # Tell Redis we successfully processed these messages
            if ids_to_ack:
                await redis.xack(CLICK_STREAM, GROUP, *ids_to_ack)

        except Exception as e:
            print(f"Worker error: {e}")
            await asyncio.sleep(5)  # Wait before retrying if DB goes down


if __name__ == "__main__":
    asyncio.run(main())