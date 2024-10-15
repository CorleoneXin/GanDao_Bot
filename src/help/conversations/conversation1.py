from fast_depends import Depends, inject
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from telegram import (ForceReply, InlineQueryResultArticle, 
                    InlineKeyboardButton, InlineKeyboardMarkup,
                    InputTextMessageContent, Update,KeyboardButton,
                    ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo)

from telegram.ext import filters,ConversationHandler
from src.bot.common.context import ApplicationContext, context_types
from src.bot.common.wrappers import command_handler,message_handler, reply_exception, any_message, ConversationBuilder
from src.bot.errors import handle_error
from src.bot.extractors import tx, load_user
from src.db.config import create_engine
from src.db.tables import User, UserRole
from src.settings import Settings
from ptbcontrib.log_forwarder import LogForwarder

import logging
import structlog 

builder = ConversationBuilder(conversation_timeout=69)
# Stages
START_ROUTES, END_ROUTES = range(2)
# Callback data
ONE, TWO, THREE, FOUR = range(4)

@builder.entry_point
@command_handler("InLineKeyBoard2")
async def entrypoint(update: Update, context: ApplicationContext):
    """Send message on `/start`."""
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(ONE)),
            InlineKeyboardButton("2", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Start handler, Choose a route", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START_ROUTES
    
@builder.state(START_ROUTES)
@any_message
async def start_over(update: Update, context: ApplicationContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(ONE)),
            InlineKeyboardButton("2", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    await query.edit_message_text(text="Start handler, Choose a route", reply_markup=reply_markup)
    return START_ROUTES


handler_nest = builder.build()