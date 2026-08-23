import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select

from app.database import async_session_factory
from app.models.collector import Collector


async def main():
    try:
        async with async_session_factory() as session:
            stmt = select(Collector).limit(10)
            print("Executing query...")
            result = await session.execute(stmt)
            collectors = result.scalars().all()
            print("Query succeeded. Collectors:", collectors)
    except Exception:
        import traceback
        print("EXCEPTION OCCURRED:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
