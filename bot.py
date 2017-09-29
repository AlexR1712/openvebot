#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot for get OpenVe Telegram Links
from uuid import uuid4

import re
import random
import requests
from bs4 import BeautifulSoup

from telegram import InlineQueryResultArticle, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Token obtenido de @botfather en Telegram
TOKEN = "TOKEN_BOT_FATHER"

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text(
        'Hola! soy un bot que permite buscar entre los grupos que se encuentran '+
        'en la OpenVe, para usarme solo debes escribir en cualquier chat @OpenVebot y colocar el nombre del grupo a buscar.')


def help(bot, update):
    update.message.reply_text('Si tienes problemas con el bot, contacta con @alexr1712 mi creador!')


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    r = requests.get('https://github.com/OpenVE/comunidades-en-telegram/blob/master/README.md')
    soup = BeautifulSoup(r.text, "html.parser")
    results = list()
    query = update.inline_query.query
    communities = soup.find_all('tr')[2:]
    if len(query) == 0:
        random.shuffle(communities)
        for tr in communities[:50]:
            td = tr.find_all('td')
            results.append(InlineQueryResultArticle(
                id=uuid4(),
                title=escape_markdown(td[0].text),
                input_message_content=InputTextMessageContent(
                    "Nombre: {}\nLink: {} \nAdmins: {}".format(escape_markdown(td[0].text),td[2].text,td[1].text)),
                url=td[2].text,
                reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton('▶️  Ir al Grupo ◀️', url=td[2].text)],
                            [InlineKeyboardButton('🔎 Encontrar Grupos', switch_inline_query_current_chat="")]
                        ])))
    
    elif len(query) > 0:
            found = 0
            for tr in communities:
                tds = tr.find_all('td')
                if query.lower() in (tds[0].text).lower():
                    found+=1
                    results.append(InlineQueryResultArticle(
                        id=uuid4(),
                        title=tds[0].text,
                        input_message_content=InputTextMessageContent(
                        "Nombre: {}\nLink: {} \nAdmins: {}".format(escape_markdown(tds[0].text),tds[2].text,tds[1].text)),
                        url=tds[2].text,
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton('▶️  Ir al Grupo ◀️', url=tds[2].text)],
                            [InlineKeyboardButton('🔎 Encontrar Grupos', switch_inline_query_current_chat="")]
                        ])))
            if found == 0:
                results.append(InlineQueryResultArticle(
                    id=uuid4(), 
                    title='No existen items con ese termino'))
    else:
        results.append(InlineQueryResultArticle(
            id=uuid4(), 
            title='No existen items'))
    update.inline_query.answer(results)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()