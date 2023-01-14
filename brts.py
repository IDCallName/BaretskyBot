import telegram
import telegram.ext

import baretskymodule as bm

import mysql.connector as mysql

#
#  BOT STARTUP
#

BOT_TOKEN = '(УДАЛЕНО)'

updater = telegram.ext.Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

#
#  CONNECTING TO MYSQL SERVER
#

try:
    hostname: str = "tabeltabel.mysql.pythonanywhere-services.com"
    username: str = "tabeltabel"
    password: str = "(УДАЛЕНО)"

    connection = mysql.connect(host=hostname, user=username, password=password, database="tabeltabel$bar_db")

except mysql.Error as err:
    print(err)

#
#  FUNCTIONS
#

# obsolete

#
#  COMMANDS
#

@bm.chat_check
def cmd_start(update, context) -> None:
    """
    Reacts on /start with a funny message
    """

    context.bot.send_message(chat_id=update.effective_chat.id, text="Я барецкий клуб")
    print(update.message.chat.id)


@bm.chat_check
def cmd_klov(update, context) -> None:
    """
    Makes repliant a klov of the day
    """

    # create and do the query
    mysql_query: str = "SELECT klov_id FROM klovs WHERE klov_date = CURRENT_DATE();"
    mysql_result: tuple = bm.mysql_makeSelectQuery(connection, mysql_query)

    # if there is no klovs of the day, create them
    if (len(mysql_result) < 2):
        replyTo = update.message.reply_to_message;

        # send tutorian message if the original one is not a reply
        if replyTo == None:
            msg = "Ответьте на сообщение клова, чтобы добавить его в кловный список"

        # adding and saving klovs
        else:
            if len(mysql_result) == 0 or mysql_result[0][0] != replyTo.from_user.id:
                # Adding the new entry to the database
                mysql_query: str = f"INSERT INTO klovs (klov_id, klov_date) VALUES ({replyTo.from_user.id}, CURRENT_DATE())"
                bm.mysql_makeUpdateQuery(connection, mysql_query)

                msg = "Клов записан"
            else:
                msg = "Этот клов уже в кловном списке"


    # send message if there are two klovs already
    else:
        msg = "Слишком много кловов на сегодня"

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


@bm.chat_check
def cmd_get_klov(update, context) -> None:
    """
    Gets two klovs of the day from DB
    """

    # create and do query
    mysql_query: str = "SELECT klov_id FROM klovs WHERE klov_date = CURRENT_DATE();"
    mysql_result: tuple = bm.mysql_makeSelectQuery(connection, mysql_query)

    # a message for zero klovs
    if (len(mysql_result) == 0):
        msg = "Не сидят кловы!"

    # a message for only one klov
    elif (len(mysql_result) == 1):
        # getting klov's username
        klov = context.bot.get_chat_member(update.message.chat.id, mysql_result[0][0]).user.username

        msg = f"Сидит клов {klov}"

    # a message for two klovs
    else:
        # getting klov's usernames
        klov1 = context.bot.get_chat_member(update.message.chat.id, mysql_result[0][0]).user.username
        klov2 = context.bot.get_chat_member(update.message.chat.id, mysql_result[1][0]).user.username

        msg = f"Два клова {klov1} и {klov2} сидят"

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


@bm.chat_check
def cmd_add_track(update, context):

    # making something readable from context.args
    argstring = " ".join(context.args)
    badargs = argstring.split(":")
    args = [arg.strip() for arg in badargs] # should come as a reply of format "/add_track track_name : track_description : track_author"

    # adding track to the DB if message is correctly formatted
    if len(args) == 3 and update.message.reply_to_message != None:
        message_id = update.message.reply_to_message.message_id

        msg = bm.Track.create_track(connection, args[0], message_id, args[1], args[2])

    # sending tutorial message otherwise
    else:
        msg = "Введите комманду в формате /add_track имя трека : описание трека : автор трека"

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


@bm.chat_check
def cmd_get_track(update, context):

    # turns args into a track name
    track_name = " ".join(context.args)

    # gets track
    track = bm.Track(connection, track_name)

    msg = f"*{track.track_name.capitalize()}*\n\n_Автор: {track.track_author}_\n\n{track.track_description}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='MarkdownV2')

    if track.track_msg != None:
        context.bot.forward_message(update.effective_chat.id, bm.CLUB_ID, track.track_msg)
    else:
        msg = "Не удалось найти трек"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)



#
#  HANDLERS
#

from telegram.ext import CommandHandler

start_handler     = CommandHandler('start', cmd_start)
klov_handler      = CommandHandler('klov', cmd_klov)
get_klov_handler  = CommandHandler('get_klov', cmd_get_klov)
add_track_handler = CommandHandler('add_track', cmd_add_track)
get_track_handler = CommandHandler('get_track', cmd_get_track)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(klov_handler)
dispatcher.add_handler(get_klov_handler)
dispatcher.add_handler(add_track_handler)
dispatcher.add_handler(get_track_handler)

#
# START POLLING
#

updater.start_polling()
