from database.models import async_session
from database.models import Config
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy import and_,func,not_
from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.sql import exists
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


class Database:

    @connection
    async def create_config(session):
        config = await session.scalar(select(Config).where(Config.id == 1))
        if config:
            return
        new_config = Config(
            gpt_model = 'gpt-4-turbo',
            role = 'Ты юридический консультант. Отвечай строго по делу, кратко и на основе предоставленных выдержек.',
            prompt = 'Ответь, пожалуйста, строго на основе этих выдержек.'
        )
        session.add(new_config)
        await session.commit()

    
    @connection
    async def get_config(session):
        config = await session.scalar(select(Config).where(Config.id == 1))
        return config
    

    @connection
    async def set_role(session,role):
        config = await session.scalar(select(Config).where(Config.id == 1))
        if config:
            config.role = role
            await session.commit()
    

    @connection
    async def set_prompt(session,prompt):
        config = await session.scalar(select(Config).where(Config.id == 1))
        if config:
            config.prompt = prompt
            await session.commit()