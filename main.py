from fastapi import FastAPI
from routes.routes import router as main_router
from database.models import async_main
import asyncio
from function.requests import Database

app = FastAPI()

app.include_router(main_router)

@app.on_event("startup")
async def on_startup():
    await async_main()
    asyncio.create_task(Database.cleanup_expired_chats())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)