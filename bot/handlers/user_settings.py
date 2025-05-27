from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import bot.app.keyboards as kb
from aiogram.enums import ChatAction
from aiogram import Bot
import random
from datetime import datetime, timedelta
from bot.app.states import Documents,Chat, Setting
from bot.functions.file_function import File
from bot.functions.embedding_fuction import Embeddings
from bot.functions.requests import Database

user = Router()

from aiogram import types
from aiogram.types import FSInputFile
import os
import asyncio





@user.callback_query(F.data == 'SetRole')
async def set_role_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer('*Напишите пожалуйста role...*',parse_mode='Markdown')
    await callback.answer()
    await state.set_state(Setting.role)


@user.message(Setting.role)
async def set_role_state(message:Message,state:FSMContext):
    role = message.text
    await Database.set_role(role)
    await message.answer(f'✅*Role успешно изменен на* `{role}`',parse_mode='Markdown')
    await state.clear()


@user.callback_query(F.data == 'SetPrompt')
async def set_prompt_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer('*Напишите пожалуйста prompt...*',parse_mode='Markdown')
    await callback.answer()
    await state.set_state(Setting.prompt)


@user.message(Setting.prompt)
async def set_promot_state(message:Message,state:FSMContext):
    prompt = message.text
    await Database.set_prompt(prompt)
    await message.answer(f'✅*Prompt успешно изменен на* `{prompt}`',parse_mode='Markdown')
    await state.clear()


@user.callback_query(F.data == 'DocList')
async def list_documets_handler(callback:CallbackQuery):
    await callback.answer()
    files = await File.get_unique_filenames()
    if not files:
        await callback.message.answer("❌ Документы не найдены.")
        return

    text = "📄 *Список документов:*\n\n"
    for i, name in enumerate(files, start=1):
        text += f"{i}. `{name}`\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()  # Убирает "часики"


@user.callback_query(F.data == 'DeleteDoc')
async def delete_doc_handler(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    await callback.message.answer('*Введите пожалуйста название документа который хотите удалить...*',parse_mode='Markdown')
    await state.set_state(Documents.delete_doc)


@user.message(Documents.delete_doc)
async def delete_doc_state(message:Message,state:FSMContext):
    filename = message.text
    file = await File.delete_all_versions_by_name(filename)
    if file == False:
        return await message.answer(f'⚠️*Файл не был найден*',parse_mode='Markdown')
    await message.answer(f'✅*Файл успешно удален*',parse_mode='Markdown')
    await state.clear()