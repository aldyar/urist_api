from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import bot.app.keyboards as kb
from aiogram.enums import ChatAction
from aiogram import Bot
import random
from datetime import datetime, timedelta
from bot.app.states import Documents,Chat
from bot.functions.file_function import File
from bot.functions.embedding_fuction import Embeddings
from bot.functions.requests import Database

user = Router()

from aiogram import types
from aiogram.types import FSInputFile
import os
import asyncio



@user.message(CommandStart())
async def cmd_start(message:Message,state:FSMContext):
    await state.clear()
    await message.answer('*Привет я тестовый бот ИИ ассистент юрист*',parse_mode='Markdown',reply_markup=kb.main_menu)


@user.callback_query(F.data == 'AddDocx')
async def send_docx_handler(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    await callback.message.answer('*Отправьте пожалуйста DOCX файл...*',parse_mode='Markdown')
    await state.set_state(Documents.wait_docx)

@user.callback_query(F.data == 'AddPdf')
async def send_docx_handler(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    await callback.message.answer('*Отправьте пожалуйста PDF файл...*',parse_mode='Markdown')
    await state.set_state(Documents.wait_pdf)

@user.message(F.text == '💬Диалог')
async def chat_handler(message:Message,state:FSMContext):
    await message.answer('*Введите ваш вопрос*',parse_mode='Markdown',reply_markup=kb.cancel)
    await state.set_state(Chat.chat)
    
@user.message(F.text == '🚪Выйти из чата')
async def cancel_handler(message:Message,state:FSMContext):
    await state.clear()
    await cmd_start(message,state)


@user.message(F.text == '⚙️Настройки')
async def settings_handler(message:Message,state:FSMContext):
    await state.clear()
    config = await Database.get_config()
    text = f"""⚙️ *Текущие настройки:*

🤖 *Модель GPT:* `{config.gpt_model}`

🧠 *Роль системы:*
_{config.role}_

📩 *Промпт:*
_{config.prompt}_

Чтобы изменить настройки, обратись к администратору или используй соответствующие команды.
"""
    
    await message.answer(text,parse_mode='Markdown',reply_markup=kb.inline_settings)

@user.message(Chat.chat)
async def chat_process_handler(message:Message,state:FSMContext):
    question = message.text
    await message.answer('Ваш запрос генерируется...')
    await message.bot.send_chat_action(chat_id=message.from_user.id,action=ChatAction.TYPING)
    data = await state.get_data()
    history = data.get('history', [])
    history.append(question)
    history = history[-20:]
    await state.update_data(history=history)
    print(f'HISTORY:______________{history}')
    joined_history = "\n".join(history)
    result = await Embeddings.load_1all_embeddings_from_folder(joined_history)
    config = await Database.get_config()
    history.append(result['answer'])
    await message.answer(f'💬*Ваш ответ от OpenAI* \n\n{result['answer']}',parse_mode='Markdown')
    await message.answer(f'*Информацию которая была использована для ответа*\n\n{result["context"]}',parse_mode='Markdown')
    await message.answer(
    f"""📊 *Статистика:*

⏱️ Время запроса к GPT: {result["metrics"]["openai_time_sec"]:.2f} сек
⏱️ Время поиска в базе знаний: {result["metrics"]["search_time_sec"]:.2f} сек
⏱️ Время выполнения скрипта: {result["metrics"]["total_time_sec"]:.2f} сек

📝 Вопрос:
   - Символов: {result["metrics"]["prompt_chars"]}
   - Токенов: {result["metrics"]["prompt_tokens"]}

🧾 Ответ:
   - Символов: {result["metrics"]["response_chars"]}
   - Токенов: {result["metrics"]["response_tokens"]}

💵 Стоимость:
   - Input: ${result["metrics"]["input_cost_usd"]:.6f}
   - Output: ${result["metrics"]["output_cost_usd"]:.6f}
   - Общая: ${result["metrics"]["total_cost_usd"]:.6f}

⚙️ Конфигурация:
   - OpenAI модель: {config.gpt_model}
   - Role: {config.role}
   - Prompt: {config.prompt}
""",
    parse_mode='Markdown')


@user.message(Documents.wait_docx)
async def wait_docx_handler(message:Message,state:FSMContext):
    if not message.document:
        await message.answer("❌ Пожалуйста, отправьте файл в формате .docx.")
        return

    if not message.document.file_name.endswith(".docx"):
        await message.answer("❌ Неверный формат файла. Требуется файл с расширением .docx.")
        return

    # Скачиваем файл
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)

    # Путь куда сохраняем
    save_dir = 'files'
    os.makedirs(save_dir, exist_ok=True)  # Создаём папку если её нет

    file_path = os.path.join(save_dir, message.document.file_name)

    # Скачиваем файл из Telegram в нужное место
    await message.bot.download_file(file.file_path, destination=file_path)
    txt =await File.docx_to_txt(file_path)
    await Embeddings.convert_txt_to_embeddings_batched(txt)
    
    await message.answer(f"✅ Файл сохранён и конвертирован в txt как `{message.document.file_name}` в `{save_dir}`.", parse_mode="Markdown")

    # Очистить состояние
    await state.clear()


@user.message(Documents.wait_pdf)
async def wait_docx_handler(message:Message,state:FSMContext):
    if not message.document:
        await message.answer("❌ Пожалуйста, отправьте файл в формате PDF.")
        return

    if not message.document.file_name.endswith(".pdf"):
        await message.answer("❌ Неверный формат файла. Требуется файл с расширением .pdf.")
        return

    # Скачиваем файл
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)

    # Путь куда сохраняем
    save_dir = 'files'
    os.makedirs(save_dir, exist_ok=True)  # Создаём папку если её нет

    file_path = os.path.join(save_dir, message.document.file_name)

    # Скачиваем файл из Telegram в нужное место
    await message.bot.download_file(file.file_path, destination=file_path)
    #await File.docx_to_txt(file_path)
    txt = await File.pdf_to_txt(file_path)
    await Embeddings.convert_txt_to_embeddings_batched(txt)

    await message.answer(f"✅ Файл сохранён и конвертирован в txt как `{message.document.file_name}` в `{save_dir}`.", parse_mode="Markdown")

    # Очистить состояние
    await state.clear()


@user.message(F.text == 'test')
async def tst(message:Message):
    await File.get_unique_filenames()