from fast_depends import Depends, inject
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from telegram import (ForceReply, InlineQueryResultArticle, 
                    InlineKeyboardButton, InlineKeyboardMarkup,
                    InputTextMessageContent, Update,KeyboardButton,
                    ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo)

from telegram.ext import filters,ConversationHandler
from src.bot.common.context import ApplicationContext, context_types
from src.bot.common.wrappers import command_handler,message_handler, reply_exception, delete_message_after
from src.bot.errors import handle_error
from src.bot.extractors import tx, load_user
from src.db.config import create_engine
from src.db.tables import User, UserRole
from src.settings import Settings
from ptbcontrib.log_forwarder import LogForwarder

import logging
import structlog

log = structlog.get_logger()
settings = Settings()  # type: ignore

@command_handler("help")
@reply_exception
@inject
async def handle_help(update: Update, context: ApplicationContext, session: AsyncSession = Depends(tx)):
    """Send a message when the command /help is issued."""
    
    helpText = '''
    Command list:
    /start
    /help - show help
    /command1 - eg: /command1 abc
    /command2 - eg: /command2 abc
    /deleteMsg - eg: /deleteMsg abc
    /WebApp
    /InLineKeyBoard2 - router
    /nested - show family
    /stop
    '''

    await context.bot.send_message(chat_id=update.effective_chat.id, text=helpText)


@command_handler("command1")
@reply_exception
@inject
async def handle_command1(update: Update, context: ApplicationContext, session: AsyncSession = Depends(tx)):
    text_caps = ' '.join(context.args).upper()
    reply = f'1-:{text_caps}'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
    
@command_handler("command2")
@reply_exception
@inject
async def handle_command2(update: Update, context: ApplicationContext, session: AsyncSession = Depends(tx)):
    text_caps = ' '.join(context.args).upper()
    reply = f'2-:{text_caps}'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

@command_handler("WebApp")
@reply_exception
@inject
async def handle_WebApp(update: Update, context: ApplicationContext, session: AsyncSession = Depends(tx)) -> None:
    """Send a message with a button that opens a the web app."""
    await update.message.reply_text(
        "Please press the button below to choose a color via the WebApp.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Open the App!",
                web_app=WebAppInfo(url="https://ideal-hideously-dinosaur.ngrok-free.app/"),
            )
        ),
    )

@message_handler(filters.StatusUpdate.WEB_APP_DATA)
# Handle incoming WebAppData
async def web_app_data(update: Update, context: ApplicationContext, session: AsyncSession = Depends(tx)) -> None:
    """Print the received data and remove the button."""
    data = update.effective_message.web_app_data.data
    await update.message.reply_html(
        text=(
            f"Receive data is: <code>{data}</code>"
        ),
        reply_markup=ReplyKeyboardRemove(),
    )
    
@command_handler("deleteMsg")
@delete_message_after
@inject
async def handle_deleteMsg(update: Update, context: ApplicationContext, session: AsyncSession = Depends(tx)):
    text_caps = ' '.join(context.args).upper()
    reply = f'3-:{text_caps}'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
