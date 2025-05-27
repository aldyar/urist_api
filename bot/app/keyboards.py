from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = '💬Диалог')],
                                          [KeyboardButton(text = '⚙️Настройки')]],resize_keyboard=True)

inline_settings = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Изменить Role',callback_data='SetRole'),
                                                         InlineKeyboardButton(text = 'Изменить Prompt',callback_data='SetPrompt')],
                                                        [InlineKeyboardButton(text = 'Добавить Docx',callback_data='AddDocx'),
                                                         InlineKeyboardButton(text = 'Добавить PDF', callback_data='AddPdf')],
                                                         [InlineKeyboardButton(text = 'Список документов',callback_data='DocList'),
                                                          InlineKeyboardButton(text = 'Удалить документ',callback_data='DeleteDoc')]])

cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = '🚪Выйти из чата')]],resize_keyboard=True)