from sqlalchemy import ForeignKey, String, BigInteger, DateTime, Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
from sqlalchemy import JSON


engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3',
                             echo=True)
    
    
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Config(Base):
    __tablename__ = 'config'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gpt_model: Mapped[str] = mapped_column(String,nullable=True)
    role: Mapped[str] = mapped_column(String,nullable=True)
    prompt: Mapped[str] = mapped_column(String,nullable=True)    

class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String)
    question: Mapped[str] = mapped_column(String)
    value: Mapped[str] = mapped_column(String,nullable=True)
    active: Mapped[bool] = mapped_column(Boolean,default=True)
    last_active:Mapped[datetime] = mapped_column(DateTime,nullable=True)
    source: Mapped[datetime] = mapped_column(String,nullable=True)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)