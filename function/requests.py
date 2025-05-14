from database.models import async_session
from database.models import Chat, Config
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime,timedelta
from sqlalchemy import and_,func
from database.storage import chat_histories
import asyncio


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


class Database:

    # @connection
    # async def set_chat(session,chat_id,question):
    #     chat = await session.scalar(select(Chat).where(Chat.chat_id == chat_id))

    #     if not chat:
    #         new_chat = Chat(
    #             chat_id = chat_id,
    #             question = question,
    #             last_active = datetime.now()
    #         )
    #         session.add(new_chat)
    #         await session.commit()

    #     elif chat.active == True:
            
    @connection
    async def get_config(session):
        config = await session.scalar(select(Config).where(Config.id == 1))
        return config
    
    @connection
    async def set_chat(session,question,chat_id,value,last_active):


        chat = Chat(
            question = str(question),
            chat_id = chat_id,
            value = value,
            last_active = datetime.fromisoformat(last_active),
            active = False
        )
        session.add(chat)
        await session.commit()

    
    async def cleanup_expired_chats():
        while True:
            now = datetime.now()
            expired = []

            for chat_id, data in chat_histories.items():
                last_active = datetime.fromisoformat(data["last_active"])
                if now - last_active > timedelta(minutes=10):  # ✅ 10 минут
                    history = data.get("history", "")
                    await Database.set_chat_without_value(history,chat_id,last_active)
                    # Здесь можно сохранить в БД, если нужно
                    print(f"Сохраняем и удаляем чат {chat_id}")
                    expired.append(chat_id)

            for chat_id in expired:
                del chat_histories[chat_id]
            await asyncio.sleep(10)  # Проверять каждую минуту


    @connection
    async def set_chat_without_value(session,history,chat_id,last_active):
        chat = await session.scalar(select(Chat).where(Chat.chat_id == chat_id))
        if chat:
            chat.question = str(history)
        else:
            chat = Chat(
            question = str(history),
            chat_id = chat_id,
            last_active = last_active,
            active = False)
            session.add(chat)

        await session.commit()