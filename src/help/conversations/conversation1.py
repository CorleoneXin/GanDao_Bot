from fast_depends import Depends, inject
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from telegram import (ForceReply, InlineQueryResultArticle, 
                    InlineKeyboardButton, InlineKeyboardMarkup,
                    InputTextMessageContent, Update,KeyboardButton,
                    ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo)

from telegram.ext import filters, CallbackQueryHandler, ConversationHandler, CommandHandler
from src.bot.common.context import ApplicationContext, context_types
from src.bot.common.wrappers import command_handler,message_handler, reply_exception, any_message
from src.bot.common.conversation import ConversationBuilder
from src.bot.errors import handle_error
from src.bot.extractors import tx, load_user
from src.db.config import create_engine
from src.db.tables import User, UserRole
from src.settings import Settings
from ptbcontrib.log_forwarder import LogForwarder

import logging
import structlog 

# Stages
START_ROUTES, END_ROUTES = range(2)
# Callback data
ONE, TWO, THREE, FOUR = range(4)

async def InLineKeyBoard2(update: Update, context: ApplicationContext):
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

async def end(update: Update, context: ApplicationContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END

async def one(update: Update, context: ApplicationContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("3", callback_data=str(THREE)),
            InlineKeyboardButton("4", callback_data=str(FOUR)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="First CallbackQueryHandler, Choose a route", reply_markup=reply_markup
    )
    return START_ROUTES

async def two(update: Update, context: ApplicationContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(ONE)),
            InlineKeyboardButton("3", callback_data=str(THREE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Second CallbackQueryHandler, Choose a route", reply_markup=reply_markup
    )
    return START_ROUTES

async def three(update: Update, context: ApplicationContext) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Yes, let's do it again!", callback_data=str(ONE)),
            InlineKeyboardButton("Nah, I've had enough ...", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Third CallbackQueryHandler. Do want to start over?", reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return END_ROUTES

async def four(update: Update, context: ApplicationContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("2", callback_data=str(TWO)),
            InlineKeyboardButton("3", callback_data=str(THREE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Fourth CallbackQueryHandler, Choose a route", reply_markup=reply_markup
    )
    return START_ROUTES


handler_nest = ConversationHandler(
    entry_points=[CommandHandler("InLineKeyBoard2", InLineKeyBoard2)],
    states={
        START_ROUTES: [
            CallbackQueryHandler(one, pattern="^" + str(ONE) + "$"),
            CallbackQueryHandler(two, pattern="^" + str(TWO) + "$"),
            CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
            CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
        ],
        END_ROUTES: [
            CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
            CallbackQueryHandler(end, pattern="^" + str(TWO) + "$"),
        ],
    },
    fallbacks=[CommandHandler("InLineKeyBoard2", InLineKeyBoard2)],
)