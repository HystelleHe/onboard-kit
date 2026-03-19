import asyncio
import sys
sys.path.insert(0, '/app')

from app.core.database import Base, engine
from app.models.models import User, Guide, Step, PageAnalysis, UsageLog

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(init_db())
